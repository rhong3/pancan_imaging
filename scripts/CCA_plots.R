### Plots for CCA results ###

# Plot ROCs barplots
library(readr)
library(ggplot2)
library(ggpubr)
library(gridExtra)
mutation <- read_csv("Results/Statistics_mutation.csv")
mutation = mutation[,c('Folder', 'Slide_ROC.95.CI_lower', 'Slide_ROC', 'Slide_ROC.95.CI_upper', 
                       'Tile_ROC.95.CI_lower', 'Tile_ROC', 'Tile_ROC.95.CI_upper')]
colnames(mutation) = gsub('Folder', 'Feature', colnames(mutation))
mutation = mutation[mutation$Feature %in% c("TP53_CCA", "ARID1A_CCA", "ARID2_CCA", "BRCA2_CCA", "CTNNB1_CCA", "EGFR_CCA", "JAK1_CCA", "KRAS_CCA",
                                            "MTOR_CCA", "NOTCH1_CCA", "NOTCH3_CCA", "PIK3CA_CCA", "PTEN_CCA", "STK11_CCA", "TP53_CCA", "ZFHX3_CCA"), ]
tumor <- read_csv("Results/Statistics_tumor.csv")
tumor = tumor[, c('Folder', 'Slide_ROC.95.CI_lower', 'Slide_ROC', 'Slide_ROC.95.CI_upper', 
                  'Tile_ROC.95.CI_lower', 'Tile_ROC', 'Tile_ROC.95.CI_upper')]
colnames(tumor) = gsub('Folder', 'Feature', colnames(tumor))
tumor = tumor[tumor$Feature=="tumor_CCA",]
stage <- read_csv("Results/Statistics_stage.csv")
stage = stage[, c('Folder', 'Slide_Multiclass_ROC.95.CI_lower', 'Slide_Multiclass_ROC', 'Slide_Multiclass_ROC.95.CI_upper',
                  'Tile_Multiclass_ROC.95.CI_lower', 'Tile_Multiclass_ROC', 'Tile_Multiclass_ROC.95.CI_upper')]
colnames(stage) = gsub('Folder', 'Feature', colnames(stage))
colnames(stage) = gsub('Multiclass_', '', colnames(stage))
grade <- read_csv("Results/Statistics_grade.csv")
grade = grade[, c('Folder', 'Slide_Multiclass_ROC.95.CI_lower', 'Slide_Multiclass_ROC', 'Slide_Multiclass_ROC.95.CI_upper',
                  'Tile_Multiclass_ROC.95.CI_lower', 'Tile_Multiclass_ROC', 'Tile_Multiclass_ROC.95.CI_upper')]
colnames(grade) = gsub('Folder', 'Feature', colnames(grade))
colnames(grade) = gsub('Multiclass_', '', colnames(grade))
nuclei <- read_csv("Results/Statistics_nuclei.csv")
nuclei = nuclei[, c('Folder', 'Slide_Multiclass_ROC.95.CI_lower', 'Slide_Multiclass_ROC', 'Slide_Multiclass_ROC.95.CI_upper',
                  'Tile_Multiclass_ROC.95.CI_lower', 'Tile_Multiclass_ROC', 'Tile_Multiclass_ROC.95.CI_upper')]
colnames(nuclei) = gsub('Folder', 'Feature', colnames(nuclei))
colnames(nuclei) = gsub('Multiclass_', '', colnames(nuclei))
necrosis <- read_csv("Results/Statistics_necrosis.csv")
necrosis = necrosis[, c('Folder', 'Slide_Multiclass_ROC.95.CI_lower', 'Slide_Multiclass_ROC', 'Slide_Multiclass_ROC.95.CI_upper',
                  'Tile_Multiclass_ROC.95.CI_lower', 'Tile_Multiclass_ROC', 'Tile_Multiclass_ROC.95.CI_upper')]
colnames(necrosis) = gsub('Folder', 'Feature', colnames(necrosis))
colnames(necrosis) = gsub('Multiclass_', '', colnames(necrosis))
cellularity <- read_csv("Results/Statistics_cellularity.csv")
cellularity = cellularity[, c('Folder', 'Slide_Multiclass_ROC.95.CI_lower', 'Slide_Multiclass_ROC', 'Slide_Multiclass_ROC.95.CI_upper',
                  'Tile_Multiclass_ROC.95.CI_lower', 'Tile_Multiclass_ROC', 'Tile_Multiclass_ROC.95.CI_upper')]
colnames(cellularity) = gsub('Folder', 'Feature', colnames(cellularity))
colnames(cellularity) = gsub('Multiclass_', '', colnames(cellularity))
origin <- read_csv("Results/Statistics_origin.csv")
origin = origin[, c('Folder', 'Slide_Multiclass_ROC.95.CI_lower', 'Slide_Multiclass_ROC', 'Slide_Multiclass_ROC.95.CI_upper',
                              'Tile_Multiclass_ROC.95.CI_lower', 'Tile_Multiclass_ROC', 'Tile_Multiclass_ROC.95.CI_upper')]
colnames(origin) = gsub('Folder', 'Feature', colnames(origin))
colnames(origin) = gsub('Multiclass_', '', colnames(origin))


all = rbind(mutation, tumor, stage, grade, nuclei, necrosis, cellularity, origin)
all = all[order(-all$Slide_ROC),]
all = na.omit(all)

### box plot Wilcoxon test
# tiles
library(ggplot2)
library(ggpubr)
todolist = c("TP53_CCA", "ARID1A_CCA", "ARID2_CCA", "BRCA2_CCA", "CTNNB1_CCA", "EGFR_CCA", "JAK1_CCA", "KRAS_CCA",
             "MTOR_CCA", "NOTCH1_CCA", "NOTCH3_CCA", "PIK3CA_CCA", "PTEN_CCA", "STK11_CCA", "TP53_CCA", "ZFHX3_CCA")
tile_all = data.frame(Prediction_score= numeric(0), True_label= character(0), feature = character(0))
for (f in todolist){
  pos = "POS_score"
  if (f == 'tumor_CCA'){
    lev = c('negative', 'tumor')
    mm = strsplit(f, '_')[[1]][1]
  } else{
    mm = strsplit(f, '_')[[1]][1]
    lev = c('negative', mm)
  }
  Test_tile <- read.csv(paste("Results/", f, "/out/Test_tile.csv", sep=''))
  Test_tile = Test_tile[, c(pos, "True_label")]
  Test_tile['feature'] = f
  levels(Test_tile$True_label) <- c(levels(Test_tile$True_label), 'negative', 'positive')
  Test_tile$True_label[Test_tile$True_label==lev[1]] = 'negative'
  Test_tile$True_label[Test_tile$True_label==lev[2]] = 'positive'
  colnames(Test_tile) = c('Prediction_score', 'True_label', 'feature')
  tile_all = rbind(tile_all, Test_tile)
}

tile_all$feature = gsub('_CCA', "", tile_all$feature)

pp = ggboxplot(tile_all, x = "feature", y = "Prediction_score",
               color = "black", fill = "True_label", palette = "grey")+ 
  stat_compare_means(method.args = list(alternative = "greater"), aes(group = True_label), label = "p.signif", label.y = 1.1) + 
  stat_compare_means(method.args = list(alternative = "greater"), aes(group = True_label), label = "p.format", label.y = 1.15) + 
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pdf(file=paste("Results/CCA_Wilcoxon_tiles.pdf", sep=''),
    width=15,height=8)
pp
dev.off()

# slides
slide_all = data.frame(Prediction_score= numeric(0), True_label= character(0), feature = character(0))
for (f in todolist){
  pos = "POS_score"
  if (f == 'tumor_6'){
    lev = c('negative', 'tumor')
    mm = f
  } else{
    mm = strsplit(f, '_')[[1]][1]
    lev = c('negative', mm)
  }
  Test_slide <- read.csv(paste("Results/", f, "/out/Test_slide.csv", sep=''))
  Test_slide = Test_slide[, c(pos, "True_label")]
  Test_slide['feature'] = f
  levels(Test_slide$True_label) <- c(levels(Test_slide$True_label), 'negative', 'positive')
  Test_slide$True_label[Test_slide$True_label==lev[1]] = 'negative'
  Test_slide$True_label[Test_slide$True_label==lev[2]] = 'positive'
  colnames(Test_slide) = c('Prediction_score', 'True_label', 'feature')
  slide_all = rbind(slide_all, Test_slide)
}

slide_all$feature = gsub('_CCA', "", slide_all$feature)

pp = ggboxplot(slide_all, x = "feature", y = "Prediction_score",
               color = "black", fill = "True_label", palette = "grey")+ 
  stat_compare_means(method.args = list(alternative = "greater"), aes(group = True_label), label = "p.signif", label.y = 1.1) + 
  stat_compare_means(method.args = list(alternative = "greater"), aes(group = True_label), label = "p.format", label.y = 1.15) + 
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pdf(file=paste("Results/CCA_Wilcoxon_slides.pdf", sep=''),
    width=15,height=8)
pp
dev.off()



all$Feature = gsub("_CCA", "", all$Feature)

# Default bar plot
ps <- ggplot(all, aes(x=reorder(Feature, -Slide_ROC), y=Slide_ROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=Slide_ROC.95.CI_lower, ymax=Slide_ROC.95.CI_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(Slide_ROC, 3)), vjust=-0.1, size=5) +labs(title="Per Slide AUROC", x="Features", y = "Per Slide AUROC")+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pt <- ggplot(all, aes(x=reorder(Feature, -Tile_ROC), y=Tile_ROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=Tile_ROC.95.CI_lower, ymax=Tile_ROC.95.CI_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(Tile_ROC, 3)), vjust=-0.1, size=5) +labs(title="Per Tile AUROC", x="Features", y = "Per Tile AUROC", size=5)+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pdf(file="Results/CCA_ROC_plot_slide.pdf",
    width=18,height=5)
grid.arrange(ps,nrow=1, ncol=1)
dev.off()

pdf(file="Results/CCA_ROC_plot_tile.pdf",
    width=18,height=5)
grid.arrange(pt,nrow=1, ncol=1)
dev.off()

print(pt)


### individual class AUROC for multiclass tasks ###
stage <- read_csv("Results/Statistics_stage.csv")
stage = stage[, grep("ROC", colnames(stage))]
stage = stage[, -grep("Multiclass_", colnames(stage))]
OUTPUT = setNames(data.frame(matrix(ncol = 7, nrow = 5)), c("Class", "slide_AUROC", "slide_AUROC_upper", "slide_AUROC_lower", "tile_AUROC", "tile_AUROC_upper", "tile_AUROC_lower"))
for (i in 0:4){
  OUTPUT[i+1, 1] = paste("stage", i, sep="_")
  OUTPUT[i+1, 2] = stage[1, paste("Slide_stage", i, "_ROC", sep="")]
  OUTPUT[i+1, 3] = stage[1, paste("Slide_stage", i, "_ROC.95.CI_upper", sep="")]
  OUTPUT[i+1, 4] = stage[1, paste("Slide_stage", i, "_ROC.95.CI_lower", sep="")]
  OUTPUT[i+1, 5] = stage[1, paste("Tile_stage", i, "_ROC", sep="")]
  OUTPUT[i+1, 6] = stage[1, paste("Tile_stage", i, "_ROC.95.CI_upper", sep="")]
  OUTPUT[i+1, 7] = stage[1, paste("Tile_stage", i, "_ROC.95.CI_lower", sep="")]
}
# Default bar plot
ps <- ggplot(OUTPUT, aes(x=Class, y=slide_AUROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=slide_AUROC_lower, ymax=slide_AUROC_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(slide_AUROC, 3)), vjust=-0.1, size=5) +labs(title="Per Slide AUROC", x="Class", y = "Per Slide AUROC")+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pt <- ggplot(OUTPUT, aes(x=Class, y=tile_AUROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=tile_AUROC_lower, ymax=tile_AUROC_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(tile_AUROC, 3)), vjust=-0.1, size=5) +labs(title="Per Tile AUROC", x="Class", y = "Per Tile AUROC", size=5)+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pdf(file="Results/CCA_Stage_ROC_plot_slide.pdf",
    width=5,height=5)
grid.arrange(ps,nrow=1, ncol=1)
dev.off()

pdf(file="Results/CCA_Stage_ROC_plot_tile.pdf",
    width=5,height=5)
grid.arrange(pt,nrow=1, ncol=1)
dev.off()


grade <- read_csv("Results/Statistics_grade.csv")
grade = grade[, grep("ROC", colnames(grade))]
grade = grade[, -grep("Multiclass_", colnames(grade))]

OUTPUT = setNames(data.frame(matrix(ncol = 7, nrow = 5)), c("Class", "slide_AUROC", "slide_AUROC_upper", "slide_AUROC_lower", "tile_AUROC", "tile_AUROC_upper", "tile_AUROC_lower"))
for (i in 0:4){
  OUTPUT[i+1, 1] = paste("grade", i, sep="_")
  OUTPUT[i+1, 2] = grade[1, paste("Slide_grade", i, "_ROC", sep="")]
  OUTPUT[i+1, 3] = grade[1, paste("Slide_grade", i, "_ROC.95.CI_upper", sep="")]
  OUTPUT[i+1, 4] = grade[1, paste("Slide_grade", i, "_ROC.95.CI_lower", sep="")]
  OUTPUT[i+1, 5] = grade[1, paste("Tile_grade", i, "_ROC", sep="")]
  OUTPUT[i+1, 6] = grade[1, paste("Tile_grade", i, "_ROC.95.CI_upper", sep="")]
  OUTPUT[i+1, 7] = grade[1, paste("Tile_grade", i, "_ROC.95.CI_lower", sep="")]
}
# Default bar plot
ps <- ggplot(OUTPUT, aes(x=Class, y=slide_AUROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=slide_AUROC_lower, ymax=slide_AUROC_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(slide_AUROC, 3)), vjust=-0.1, size=5) +labs(title="Per Slide AUROC", x="Class", y = "Per Slide AUROC")+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pt <- ggplot(OUTPUT, aes(x=Class, y=tile_AUROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=tile_AUROC_lower, ymax=tile_AUROC_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(tile_AUROC, 3)), vjust=-0.1, size=5) +labs(title="Per Tile AUROC", x="Class", y = "Per Tile AUROC", size=5)+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pdf(file="Results/CCA_grade_ROC_plot_slide.pdf",
    width=5,height=5)
grid.arrange(ps,nrow=1, ncol=1)
dev.off()

pdf(file="Results/CCA_grade_ROC_plot_tile.pdf",
    width=5,height=5)
grid.arrange(pt,nrow=1, ncol=1)
dev.off()


nuclei <- read_csv("Results/Statistics_nuclei.csv")
nuclei = nuclei[, grep("ROC", colnames(nuclei))]
nuclei = nuclei[, -grep("Multiclass_", colnames(nuclei))]

OUTPUT = setNames(data.frame(matrix(ncol = 7, nrow = 3)), c("Class", "slide_AUROC", "slide_AUROC_upper", "slide_AUROC_lower", "tile_AUROC", "tile_AUROC_upper", "tile_AUROC_lower"))
category = c("0_49", "50_79", "80_100")
for (i in 1:3){
  OUTPUT[i, 1] = paste("nuclei", category[i], sep="_")
  OUTPUT[i, 2] = nuclei[1, paste("Slide_", category[i], "_score_ROC", sep="")]
  OUTPUT[i, 3] = nuclei[1, paste("Slide_", category[i], "_score_ROC.95.CI_upper", sep="")]
  OUTPUT[i, 4] = nuclei[1, paste("Slide_", category[i], "_score_ROC.95.CI_lower", sep="")]
  OUTPUT[i, 5] = nuclei[1, paste("Tile_", category[i], "_score_ROC", sep="")]
  OUTPUT[i, 6] = nuclei[1, paste("Tile_", category[i], "_score_ROC.95.CI_upper", sep="")]
  OUTPUT[i, 7] = nuclei[1, paste("Tile_", category[i], "_score_ROC.95.CI_lower", sep="")]
}
# Default bar plot
ps <- ggplot(OUTPUT, aes(x=Class, y=slide_AUROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=slide_AUROC_lower, ymax=slide_AUROC_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(slide_AUROC, 3)), vjust=-0.1, size=5) +labs(title="Per Slide AUROC", x="Class", y = "Per Slide AUROC")+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pt <- ggplot(OUTPUT, aes(x=Class, y=tile_AUROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=tile_AUROC_lower, ymax=tile_AUROC_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(tile_AUROC, 3)), vjust=-0.1, size=5) +labs(title="Per Tile AUROC", x="Class", y = "Per Tile AUROC", size=5)+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pdf(file="Results/CCA_nuclei_ROC_plot_slide.pdf",
    width=5,height=5)
grid.arrange(ps,nrow=1, ncol=1)
dev.off()

pdf(file="Results/CCA_nuclei_ROC_plot_tile.pdf",
    width=5,height=5)
grid.arrange(pt,nrow=1, ncol=1)
dev.off()


necrosis <- read_csv("Results/Statistics_necrosis.csv")
necrosis = necrosis[, grep("ROC", colnames(necrosis))]
necrosis = necrosis[, -grep("Multiclass_", colnames(necrosis))]

OUTPUT = setNames(data.frame(matrix(ncol = 7, nrow = 3)), c("Class", "slide_AUROC", "slide_AUROC_upper", "slide_AUROC_lower", "tile_AUROC", "tile_AUROC_upper", "tile_AUROC_lower"))
category = c("0", "1_9", "10_100")
for (i in 1:3){
  OUTPUT[i, 1] = paste("necrosis", category[i], sep="_")
  OUTPUT[i, 2] = necrosis[1, paste("Slide_", category[i], "_score_ROC", sep="")]
  OUTPUT[i, 3] = necrosis[1, paste("Slide_", category[i], "_score_ROC.95.CI_upper", sep="")]
  OUTPUT[i, 4] = necrosis[1, paste("Slide_", category[i], "_score_ROC.95.CI_lower", sep="")]
  OUTPUT[i, 5] = necrosis[1, paste("Tile_", category[i], "_score_ROC", sep="")]
  OUTPUT[i, 6] = necrosis[1, paste("Tile_", category[i], "_score_ROC.95.CI_upper", sep="")]
  OUTPUT[i, 7] = necrosis[1, paste("Tile_", category[i], "_score_ROC.95.CI_lower", sep="")]
}
# Default bar plot
ps <- ggplot(OUTPUT, aes(x=Class, y=slide_AUROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=slide_AUROC_lower, ymax=slide_AUROC_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(slide_AUROC, 3)), vjust=-0.1, size=5) +labs(title="Per Slide AUROC", x="Class", y = "Per Slide AUROC")+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pt <- ggplot(OUTPUT, aes(x=Class, y=tile_AUROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=tile_AUROC_lower, ymax=tile_AUROC_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(tile_AUROC, 3)), vjust=-0.1, size=5) +labs(title="Per Tile AUROC", x="Class", y = "Per Tile AUROC", size=5)+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pdf(file="Results/CCA_necrosis_ROC_plot_slide.pdf",
    width=5,height=5)
grid.arrange(ps,nrow=1, ncol=1)
dev.off()

pdf(file="Results/CCA_necrosis_ROC_plot_tile.pdf",
    width=5,height=5)
grid.arrange(pt,nrow=1, ncol=1)
dev.off()


cellularity <- read_csv("Results/Statistics_cellularity.csv")
cellularity = cellularity[, grep("ROC", colnames(cellularity))]
cellularity = cellularity[, -grep("Multiclass_", colnames(cellularity))]

OUTPUT = setNames(data.frame(matrix(ncol = 7, nrow = 3)), c("Class", "slide_AUROC", "slide_AUROC_upper", "slide_AUROC_lower", "tile_AUROC", "tile_AUROC_upper", "tile_AUROC_lower"))
category = c("0_79", "80_89", "90_100")
for (i in 1:3){
  OUTPUT[i, 1] = paste("cellularity", category[i], sep="_")
  OUTPUT[i, 2] = cellularity[1, paste("Slide_", category[i], "_score_ROC", sep="")]
  OUTPUT[i, 3] = cellularity[1, paste("Slide_", category[i], "_score_ROC.95.CI_upper", sep="")]
  OUTPUT[i, 4] = cellularity[1, paste("Slide_", category[i], "_score_ROC.95.CI_lower", sep="")]
  OUTPUT[i, 5] = cellularity[1, paste("Tile_", category[i], "_score_ROC", sep="")]
  OUTPUT[i, 6] = cellularity[1, paste("Tile_", category[i], "_score_ROC.95.CI_upper", sep="")]
  OUTPUT[i, 7] = cellularity[1, paste("Tile_", category[i], "_score_ROC.95.CI_lower", sep="")]
}
# Default bar plot
ps <- ggplot(OUTPUT, aes(x=Class, y=slide_AUROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=slide_AUROC_lower, ymax=slide_AUROC_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(slide_AUROC, 3)), vjust=-0.1, size=5) +labs(title="Per Slide AUROC", x="Class", y = "Per Slide AUROC")+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pt <- ggplot(OUTPUT, aes(x=Class, y=tile_AUROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=tile_AUROC_lower, ymax=tile_AUROC_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(tile_AUROC, 3)), vjust=-0.1, size=5) +labs(title="Per Tile AUROC", x="Class", y = "Per Tile AUROC", size=5)+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pdf(file="Results/CCA_cellularity_ROC_plot_slide.pdf",
    width=5,height=5)
grid.arrange(ps,nrow=1, ncol=1)
dev.off()

pdf(file="Results/CCA_cellularity_ROC_plot_tile.pdf",
    width=5,height=5)
grid.arrange(pt,nrow=1, ncol=1)
dev.off()


