### CCA project figures
library(ComplexHeatmap)
library(dplyr)
library(readr)
library(circlize)
library(ggplot2)

# Figure1A heatmaps
necrosis = read.csv("DLCCA/necrosis.csv")[, c("Slide_ID", "Tumor", "set", "Percent_Necrosis")]
cellularity = read.csv("DLCCA/cellularity.csv")[, c("Slide_ID", "Tumor", "set", "Percent_Total_Cellularity")]
nuclei = read.csv("DLCCA/tumor_nuclei.csv")[, c("Slide_ID", "Tumor", "set", "Percent_Tumor_Nuclei")]
mutation = read.csv("DLCCA/mutations.csv")[, c("Slide_ID", "Tumor", "set", "ARID1A", "ARID2", "BRCA2", "CTNNB1", "EGFR", "JAK1", "KRAS",
                                               "MAP3K1", "MTOR", "NOTCH1", "NOTCH3", "PIK3CA", "PTEN", "STK11", "TP53", "ZFHX3")]
stage = read.csv("DLCCA/stage.csv")[, c("Slide_ID", "Tumor", "set", "Stage")]
tmnm = read.csv("DLCCA/tumor_normal.csv")[, c("Slide_ID", "Tumor", "set", "Tumor_normal")]
grade = read.csv("DLCCA/grade.csv")[, c("Slide_ID", "Tumor", "set", "grade")]
colnames(grade) = c("Slide_ID", "Tumor", "set", "Grade")
 
joint = grade %>%
  full_join(tmnm , by=c("Slide_ID", "Tumor", "set")) %>%
  full_join(stage , by=c("Slide_ID", "Tumor", "set")) %>%
  full_join(necrosis , by=c("Slide_ID", "Tumor", "set")) %>%
  full_join(cellularity , by=c("Slide_ID", "Tumor", "set")) %>%
  full_join(nuclei , by=c("Slide_ID", "Tumor", "set")) %>%
  full_join(mutation , by=c("Slide_ID", "Tumor", "set")) %>%
  arrange(desc(Tumor_normal), set)

colnames(joint)[2:9] = c("Tumor", "Set", "Grade", "Tumor_normal", "Stage", "Necrosis%", "Cellularity%", "Tumor_Nuclei%")

joint = joint[, c(1,3,2,4:25)]

write.csv(joint, "DLCCA/summary.csv")


## Heatmap for tumor samples only
joint.fig = joint[joint["Tumor_normal"] == 1, -c(1,5)]

joint.fig = joint.fig[rowSums(is.na(joint.fig)) != ncol(joint.fig), ]

joint.fig = joint.fig[joint.fig["Set"] == "validation", -c(1)]

binaries = c('gray90','gray10')

get_color = function(colors,factor){
  levels=levels(factor)
  print(levels)
  res = colors[unique(as.numeric(sort(factor)))]
  res = res[!is.na(res)]
  names(res) = levels
  print(res)
  return(res)
}

joint.fig[,7:22] = lapply(joint.fig[,7:22],
                               function(x)as.factor(x))
ColSide=lapply(joint.fig[,7:22],
               function(x)get_color(binaries,x))
# tissueOrigin= c('CCRCC' = '#ff7f0e', 'HNSCC' = '#902020','LSCC' = '#41e0d1','LUAD' = '#cb997e', 'PDA' = '#9566bd','UCEC' = '#ff0101’)
ColSide[['Tumor']]=get_color(colors=c('#ff7f0e','#902020','#41e0d1','#cb997e','#9566bd','#ff0101'),
                             factor=joint.fig$Tumor)

# ColSide[['Set']]=get_color(colors=c('#8dd3c7','#ffffb3', '#bebada'),
#                                  factor = joint.fig$Set)

ColSide[['Grade']]=get_color(colors=c('#f1eef6', '#d7b5d8', '#df65b0', '#ce1256'), 
                            factor = as.factor(joint.fig$Grade))

ColSide[['Stage']]=get_color(colors=c("#ffffcc","#c2e699","#78c679","#238443"), factor=as.factor(joint.fig$Stage))

ColSide[['Necrosis%']]=colorRamp2(breaks=range(joint.fig$`Necrosis%`, na.rm=T),
                            colors=c("#eff3ff","#2171b5"))
ColSide[['Cellularity%']]=colorRamp2(breaks=range(joint.fig$`Cellularity%`, na.rm=T),
                            colors=c("#fee5d9","#cb181d"))

ColSide[['Tumor_Nuclei%']]=colorRamp2(breaks=range(joint.fig$`Tumor_Nuclei%`, na.rm=T),
                                                  colors=c("#f2f0f7","#6a51a3"))

ca = HeatmapAnnotation(df = joint.fig[order(joint.fig$Tumor), ], na_col ='white',
                       which = 'column',
                       annotation_name_gp = gpar(fontsize =18,fontface='bold'),
                       annotation_height = unit(rep(1,length(ColSide)), "inch"),
                       border = F,
                       gap = unit(rep(0.1,length(ColSide)), "inch"),
                       annotation_legend_param = list(title_gp = gpar(fontsize = 22,fontface = 'bold'),
                                                      labels_gp = gpar(fontsize = 18),
                                                      direction='horizontal',
                                                      #nrow =2, ncol=10,
                                                      grid_width= unit(0.3,'inch'),
                                                      grid_height = unit(0.3,'inch')
                       ),
                       col = ColSide,
                       show_annotation_name =T)

ph = matrix(NA ,ncol=nrow(joint.fig),nrow=0)

plot_heatmap=Heatmap(ph[,order(joint.fig$Tumor)], 
                     top_annotation = ca, cluster_columns = F, cluster_rows = F, show_heatmap_legend = F)


out_dir = 'DLCCA/Figures/Figure1-S1/'
pdf(file = paste(out_dir,'ValidationsummaryHM_tumor.pdf',sep='/'),
    width =25, height = 10, bg='white')
draw(plot_heatmap, annotation_legend_side = "bottom")
graphics.off()


# Bar plot for normal samples
joint.nor = joint[joint["Tumor_normal"] !=1, c(2,3)]
joint.nor = joint.nor[rowSums(is.na(joint.nor)) != ncol(joint.nor), ]
joint.sum = joint.nor %>%
  count(Tumor, Set, sort=F)
colnames(joint.sum) = c("Tumor", "Set", "normal_sample_count")

p = ggplot(joint.sum, aes(x=Tumor, y=normal_sample_count, fill=Set))+
  geom_bar(stat="identity", position=position_dodge())+
  geom_text(aes(label=normal_sample_count), vjust=1, position = position_dodge(0.9),
                                                                 color="black", size=3.5)+
  theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                     panel.grid.minor = element_blank(), 
                     axis.line = element_line(colour = "black"), legend.position='bottom')+
  scale_fill_manual(values=c('#8dd3c7','#ffffb3', '#bebada'))

out_dir = 'DLCCA/Figure1-S1/'
pdf(file = paste(out_dir,'normal_count.pdf',sep='/'),
    width =15, height = 5, bg='white')
p
graphics.off()



# Mutation rate summary
# mutation rate
library("tidyr")

CCA_cohort = read.csv("DLCCA/summary.csv")
CCA_cohort$Patient_ID = substr(as.character(CCA_cohort$Slide_ID),1,nchar(as.character(CCA_cohort$Slide_ID))-3)
CCA_cohort = unique(CCA_cohort[, c("Tumor", "Patient_ID")])


mutation = read.csv('~/documents/pancan_imaging/mutation_label.csv')
mutation = mutation[, c('Patient_ID', 'Tumor', 'STK11', 'KRAS', 'EGFR', 'TP53', 'PTEN', 'CTNNB1', 'ARID1A', 'PIK3CA', 'NOTCH1', 
                        'ZFHX3', 'ARID2', 'BRCA2', 'JAK1', 'MAP3K1', 'MTOR', 'NOTCH3')]
mutation = mutation[mutation$Patient_ID %in% CCA_cohort$Patient_ID, ]

mutation = unique(mutation)
mutation = mutation[,-1]

mutation.tab = mutation %>%
  group_by(Tumor) %>%
  summarise_all(mean, na.rm = TRUE)

mut = as.data.frame(mutation.tab[,c('Tumor', colnames(mutation.tab)[2])])
colnames(mut) = c('type', 'mutation rate')
mut$gene = colnames(mutation.tab)[2]
for (i in 3:ncol(mutation.tab)){
  mutx = as.data.frame(mutation.tab[,c('Tumor', colnames(mutation.tab)[i])])
  colnames(mutx) = c('type', 'mutation rate')
  mutx$gene = colnames(mutation.tab)[i]
  mut = rbind.data.frame(mut, mutx)
}

mut$`mutation rate` = as.numeric(as.character(mut$`mutation rate`))*100
mut$`mutation rate`=replace_na(mut$`mutation rate`, 0)

# tissueOrigin= c('CCRCC' = '#ff7f0e','GBM' = '#818081', 'HNSCC' = '#902020','LSCC' = '#41e0d1','LUAD' = '#cb997e', 'PDA' = '#9566bd','UCEC' = '#ff0101')

pdf(file='DLCCA/Figure1-S1/mutation_summary.pdf', 
    width=12,height=4)
ggplot(mut, aes(x=gene, y=`mutation rate`, fill=type))+
  geom_bar(stat="identity", color="black", position=position_dodge())+
  geom_text(aes(label=round(`mutation rate`)), vjust=0, color="black",
            position = position_dodge(1), size=2) +
  theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                     panel.grid.minor = element_blank(), 
                     axis.line = element_line(colour = "black"), legend.position='bottom')+
  scale_fill_manual(values=c('#ff7f0e','#902020', '#41e0d1','#cb997e', '#9566bd', '#ff0101'))
dev.off()






