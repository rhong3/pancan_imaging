## Heatmap cross-testing
library(ggplot2)

Statistics_CCA_cross <- read.csv("~/Documents/pancan_imaging/Results/Statistics_CCA_cross.csv") 

TP53 = Statistics_CCA_cross[Statistics_CCA_cross$Feature=='TP53', c('Model', 'On', 'Slide_ROC', 'Tile_ROC')]
Tumor = Statistics_CCA_cross[Statistics_CCA_cross$Feature=='Tumor', c('Model', 'On', 'Slide_ROC', 'Tile_ROC')]

TP53[,c(3,4)] = round(TP53[,c(3,4)], digits=3)
Tumor[,c(3,4)] = round(Tumor[,c(3,4)], digits=3)

# Create a ggheatmap
ggheatmap <- ggplot(TP53, aes(Model, On, fill = Slide_ROC))+
  geom_tile(color = "white")+
  scale_fill_gradient2(low = "blue", high = "red", mid = "white", 
                       midpoint = 0.5, limit = c(0,1), space = "Lab", 
                       name="") +
  theme_minimal()+ # minimal theme
  theme(axis.text.x = element_text(angle = 45, vjust = 1, 
                                   size = 12, hjust = 1))+
  coord_fixed()

ggheatmap + 
  geom_text(aes(Model, On, label = Slide_ROC), color = "black", size = 4) +
  theme(plot.title = element_text(hjust = 0.5),
    panel.grid.major = element_blank(),
    panel.border = element_blank(),
    panel.background = element_blank(),
    axis.ticks = element_blank(),
    legend.position = "none")+
  guides(fill = guide_colorbar(barwidth = 7, barheight = 1,
                               title.position = "top", title.hjust = 0.5)) + ggtitle("Tumor vs. Normal Slide AUROC") + 
  xlab('Trained on') + ylab('Applied to')

### Legacy ###
# label$path = as.character(label$path)
# for (i in 1:nrow(label)){
#   label$path[i] = paste('../tiles', as.character(label$Tumor[i]), as.character(label$Patient_ID[i]), strsplit(as.character(label$Slide_ID[i]), split='-')[[1]][3], '', sep='/')
# }
# write.csv(label, '~/documents/pancan_imaging/DLCCA/tumor_normal.csv', row.names = FALSE)
