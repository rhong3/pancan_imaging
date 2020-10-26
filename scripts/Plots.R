# Plot ROCs barplots
library(readr)
library(ggplot2)
library(ggpubr)
library(gridExtra)
mutation <- read_csv("Results/Statistics_mutation.csv")
mutation = mutation[,c('Gene', 'Slide_ROC.95.CI_lower', 'Slide_ROC', 'Slide_ROC.95.CI_upper', 
                       'Tile_ROC.95.CI_lower', 'Tile_ROC', 'Tile_ROC.95.CI_upper')]
colnames(mutation) = gsub('Gene', 'Feature', colnames(mutation))
tumor <- read_csv("Results/Statistics_tumor.csv")
tumor = tumor[4, c('Folder', 'Slide_ROC.95.CI_lower', 'Slide_ROC', 'Slide_ROC.95.CI_upper', 
                       'Tile_ROC.95.CI_lower', 'Tile_ROC', 'Tile_ROC.95.CI_upper')]
colnames(tumor) = gsub('Folder', 'Feature', colnames(tumor))
other <- read_csv("Results/Statistics_other.csv")
other = other[, c('Feature', 'Slide_ROC.95.CI_lower', 'Slide_ROC', 'Slide_ROC.95.CI_upper', 
                   'Tile_ROC.95.CI_lower', 'Tile_ROC', 'Tile_ROC.95.CI_upper')]
all = rbind(mutation, tumor, other)
all$Feature = gsub('tumor_10', 'tumor', all$Feature)

# Default bar plot
ps <- ggplot(all, aes(x=Feature, y=Slide_ROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=Slide_ROC.95.CI_lower, ymax=Slide_ROC.95.CI_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(Slide_ROC, 2)), vjust=-0.5, size=3.5) +labs(title="Per Slide AUROC", x="Features", y = "Per Slide AUROC")+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5))

pt <- ggplot(all, aes(x=Feature, y=Tile_ROC)) + 
  geom_bar(stat="identity", color="black", 
           position=position_dodge()) +
  geom_errorbar(aes(ymin=Tile_ROC.95.CI_lower, ymax=Tile_ROC.95.CI_upper), width=.2,
                position=position_dodge(.9)) +
  geom_text(aes(label=round(Tile_ROC, 2)), vjust=-0.5, size=3.5) +labs(title="Per Tile AUROC", x="Features", y = "Per Tile AUROC")+
  theme_classic() +
  scale_fill_manual(values=c("#808080")) + theme(plot.title = element_text(hjust = 0.5))

pdf(file="Results/ROC_plot.pdf",
    width=15,height=5)
grid.arrange(ps,pt,nrow=1, ncol=2)
dev.off()


# box plot Wilcoxon test
