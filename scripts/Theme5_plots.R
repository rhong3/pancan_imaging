# Plot ROCs barplots
library(readr)
library(ggplot2)
library(ggpubr)
library(gridExtra)
library(dplyr)

other <- read_csv("Results/Statistics_other.csv")
other = other[, c('Folder', 'Slide_ROC.95.CI_lower', 'Slide_ROC', 'Slide_ROC.95.CI_upper',
                  'Tile_ROC.95.CI_lower', 'Tile_ROC', 'Tile_ROC.95.CI_upper')]
colnames(other) = gsub('Folder', 'Feature', colnames(other))

other = filter(other, !grepl("8c", Feature))
other = filter(other, !grepl("8p", Feature))
other = filter(other, !grepl("8q", Feature))
all = other[order(-other$Slide_ROC),]
all = na.omit(all)

# Default bar plot
ps <- ggplot(all, aes(x=reorder(Feature, -Slide_ROC), y=Slide_ROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=Slide_ROC.95.CI_lower, ymax=Slide_ROC.95.CI_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(Slide_ROC, 2)), vjust=-0.1, size=5) +labs(title="Per Slide AUROC", x="Features", y = "Per Slide AUROC")+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pt <- ggplot(all, aes(x=reorder(Feature, -Tile_ROC), y=Tile_ROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=Tile_ROC.95.CI_lower, ymax=Tile_ROC.95.CI_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(Tile_ROC, 2)), vjust=-0.1, size=5) +labs(title="Per Tile AUROC", x="Features", y = "Per Tile AUROC", size=5)+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5), axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pdf(file="Results/Theme5_ROC_plot_slide.pdf",
    width=10,height=5)
grid.arrange(ps,nrow=1, ncol=1)
dev.off()

pdf(file="Results/Theme5_ROC_plot_tile.pdf",
    width=10,height=5)
grid.arrange(pt,nrow=1, ncol=1)
dev.off()

# box plot Wilcoxon test
# tiles
library(ggplot2)
library(ggpubr)
todolist = all$Feature
tile_all = data.frame(Prediction_score= numeric(0), True_label= character(0), feature = character(0))
for (f in todolist){
  pos = "POS_score"
  if (grepl("P", f, fixed=TRUE)){
    mm = paste('Protein_', strsplit(f, "P")[[1]][2], sep='')
    lev = c('negative', mm)
  } else if (grepl("R", f, fixed=TRUE)){
    mm = paste('RNA_', strsplit(f, "R")[[1]][2], sep='')
    lev = c('negative', mm)
  } else{
    lev = c('negative', f)
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


for (m in c("IC001", "IC013", "IC005", "IC031", "IC039")){
  tile_all$True_label = gsub(m, "positive", tile_all$True_label)
}

pp = ggboxplot(tile_all, x = "feature", y = "Prediction_score",
               color = "black", fill = "True_label", palette = "grey")+ 
  stat_compare_means(method.args = list(alternative = "less"), aes(group = True_label), label = "p.signif", label.y = 1.1) + 
  stat_compare_means(method.args = list(alternative = "less"), aes(group = True_label), label = "p.format", label.y = 1.15) + 
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pdf(file=paste("Results/Theme5_Wilcoxon_tiles.pdf", sep=''),
    width=20,height=8)
grid.arrange(pp,nrow=1)
dev.off()

# slides
slide_all = data.frame(Prediction_score= numeric(0), True_label= character(0), feature = character(0))
for (f in todolist){
  pos = "POS_score"
  if (grepl("P", f, fixed=TRUE)){
    mm = paste('Protein_', strsplit(f, "P")[[1]][2], sep='')
    lev = c('negative', mm)
  } else if (grepl("R", f, fixed=TRUE)){
    mm = paste('RNA_', strsplit(f, "R")[[1]][2], sep='')
    lev = c('negative', mm)
  } else{
    lev = c('negative', f)
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

for (m in c("IC001", "IC013", "IC005", "IC031", "IC039")){
  slide_all$True_label = gsub(m, "positive", slide_all$True_label)
}

pp = ggboxplot(slide_all, x = "feature", y = "Prediction_score",
               color = "black", fill = "True_label", palette = "grey")+ 
  stat_compare_means(method.args = list(alternative = "less"), aes(group = True_label), label = "p.signif", label.y = 1.1) + 
  stat_compare_means(method.args = list(alternative = "less"), aes(group = True_label), label = "p.format", label.y = 1.15) + 
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size=15, face="bold"))

pdf(file=paste("Results/Theme5_Wilcoxon_slides.pdf", sep=''),
    width=20,height=8)
grid.arrange(pp,nrow=1)
dev.off()
