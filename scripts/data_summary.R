# Pan-cancer Data Summary
library(dplyr)
library(ggplot2)
library(tidyr)

patient = read.csv('~/documents/pancan_imaging/patient_summary.csv')
patient.a = patient[, c(1,2)]
patient.a$set = 'all'
patient.b = patient[, c(1,3)]
patient.b$set = "data freeze"
colnames(patient.b) = c('type', 'patient_count', 'set')
patient = rbind(patient.a, patient.b)

pdf(file='~/documents/pancan_imaging/patient_summary.pdf', 
    width=8,height=4)
ggplot(patient, aes(x=type, y=patient_count, fill=set))+
  geom_bar(stat="identity", color="black", position=position_dodge())+
  geom_text(aes(label=patient_count), vjust=1.6, color="black",
            position = position_dodge(0.9), size=3.5) +
  theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                     panel.grid.minor = element_blank(), 
                     axis.line = element_line(colour = "black"), legend.position='bottom')
dev.off()

slide = read.csv('~/documents/pancan_imaging/slide_summary_df.csv')
slide = slide[, c(1,3)]
slide = slide %>%
  group_by(type) %>%
  summarise(slide = sum(slide_count), ave=mean(slide_count), std=sd(slide_count))

colnames(slide) = c('type', "slide_count", 'slides_per_patient', 'std')

pdf(file='~/documents/pancan_imaging/slide_summary.pdf', 
    width=5,height=3)
ggplot(slide, aes(x=type, y=slide_count))+
  geom_bar(stat="identity", fill='#999999', color='black')+
  geom_text(aes(label=slide_count), vjust=1.6, color="white",
            position = position_dodge(0.9), size=3.5) +
  theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                     panel.grid.minor = element_blank(), 
                     axis.line = element_line(colour = "black"), legend.position='bottom')
dev.off()


pdf(file='~/documents/pancan_imaging/slide_per_patient.pdf', 
    width=5,height=3)
ggplot(slide, aes(x=type, y=slides_per_patient))+
  geom_bar(stat="identity", fill='#999999', color='black') +
  geom_errorbar(aes(ymin=slides_per_patient-std, ymax=slides_per_patient+std), width=.2,
                position=position_dodge(.9))+
  theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                     panel.grid.minor = element_blank(), 
                     axis.line = element_line(colour = "black"), legend.position='bottom')
dev.off()


# mutation rate
mutation = read.csv('~/documents/pancan_imaging/mutation_label.csv')
mutation = mutation[, c('Patient_ID', 'Tumor', 'STK11', 'KRAS', 'EGFR', 'TP53', 'PTEN', 'CTNNB1', 'ARID1A', 'PIK3CA', 'NOTCH1', 
                        'ZFHX3', 'ARID2', 'BRCA2', 'JAK1', 'MAP3K1', 'MTOR', 'NOTCH3')]
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
mut = na.omit(mut)
# mut$`mutation rate`=replace_na(mut$`mutation rate`, 0)

pdf(file='~/documents/pancan_imaging/key_mutation_summary.pdf', 
    width=12,height=4)
ggplot(mut, aes(x=gene, y=`mutation rate`, fill=type))+
  geom_bar(stat="identity", color="black", position=position_dodge())+
  geom_text(aes(label=round(mut$`mutation rate`)), vjust=0, color="black",
            position = position_dodge(1), size=2) +
  theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
                     panel.grid.minor = element_blank(), 
                     axis.line = element_line(colour = "black"), legend.position='bottom')
dev.off()

