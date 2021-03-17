# Plot ROCs barplots
library(readr)
library(ggplot2)
library(ggpubr)
library(gridExtra)
mutation <- read_csv("Results/Statistics_mutation.csv")
mutation = mutation[,c('Folder', 'Slide_ROC.95.CI_lower', 'Slide_ROC', 'Slide_ROC.95.CI_upper', 
                       'Tile_ROC.95.CI_lower', 'Tile_ROC', 'Tile_ROC.95.CI_upper')]
colnames(mutation) = gsub('Folder', 'Feature', colnames(mutation))
tumor <- read_csv("Results/Statistics_tumor.csv")
tumor = tumor[, c('Folder', 'Slide_ROC.95.CI_lower', 'Slide_ROC', 'Slide_ROC.95.CI_upper', 
                       'Tile_ROC.95.CI_lower', 'Tile_ROC', 'Tile_ROC.95.CI_upper')]
colnames(tumor) = gsub('Folder', 'Feature', colnames(tumor))
other <- read_csv("Results/Statistics_other.csv")
other = other[, c('Folder', 'Slide_ROC.95.CI_lower', 'Slide_ROC', 'Slide_ROC.95.CI_upper',
                   'Tile_ROC.95.CI_lower', 'Tile_ROC', 'Tile_ROC.95.CI_upper')]
colnames(other) = gsub('Folder', 'Feature', colnames(other))
all = rbind(mutation, tumor, other)
# all$Feature = gsub('tumor_6', 'tumor', all$Feature)
all = all[order(-all$Slide_ROC),]
all = na.omit(all)

# Default bar plot
ps <- ggplot(all, aes(x=reorder(Feature, -Slide_ROC), y=Slide_ROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=Slide_ROC.95.CI_lower, ymax=Slide_ROC.95.CI_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(Slide_ROC, 2)), vjust=-0.5, size=3.5) +labs(title="Per Slide AUROC", x="Features", y = "Per Slide AUROC")+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5))

pt <- ggplot(all, aes(x=reorder(Feature, -Tile_ROC), y=Tile_ROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=Tile_ROC.95.CI_lower, ymax=Tile_ROC.95.CI_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(Tile_ROC, 2)), vjust=-0.5, size=3.5) +labs(title="Per Tile AUROC", x="Features", y = "Per Tile AUROC")+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5))

pdf(file="Results/ROC_plot.pdf",
    width=35,height=5)
grid.arrange(ps,pt,nrow=1, ncol=2)
dev.off()


# box plot Wilcoxon test
# tiles
library(ggplot2)
library(ggpubr)
todolist = all$Feature
tile_all = data.frame(Prediction_score= numeric(0), True_label= character(0), feature = character(0))
for (f in todolist){
    pos = "POS_score"
    if (f == 'tumor_6'){
      lev = c('negative', 'tumor')
      mm = f
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

pp = ggboxplot(tile_all, x = "feature", y = "Prediction_score",
               color = "black", fill = "True_label", palette = "grey")+ 
  stat_compare_means(method.args = list(alternative = "greater"), aes(group = True_label), label = "p.signif", label.y = 1.1) + 
  stat_compare_means(method.args = list(alternative = "greater"), aes(group = True_label), label = "p.format", label.y = 1.15) + 
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

pdf(file=paste("Results/Wilcoxon_tiles.pdf", sep=''),
    width=30,height=8)
grid.arrange(pp,nrow=1)
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

pp = ggboxplot(slide_all, x = "feature", y = "Prediction_score",
               color = "black", fill = "True_label", palette = "grey")+ 
  stat_compare_means(method.args = list(alternative = "greater"), aes(group = True_label), label = "p.signif", label.y = 1.1) + 
  stat_compare_means(method.args = list(alternative = "greater"), aes(group = True_label), label = "p.format", label.y = 1.15) + 
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

pdf(file=paste("Results/Wilcoxon_slides.pdf", sep=''),
    width=30,height=8)
grid.arrange(pp,nrow=1)
dev.off()


