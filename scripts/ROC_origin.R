# ROC origin
library(pROC)

cancer = c('CCRCC', 'HNSCC', 'LSCC', 'LUAD', 'PDA', 'UCEC')
color = c('#ff7f0e', '#902020', '#41e0d1', '#cb997e', '#9566bd', '#ff0101')
  
Test_tile = read.csv(paste("~/documents/pancan_imaging/Results/origin_CCA/out/Test_tile.csv", sep=''))
Test_slide = read.csv(paste("~/documents/pancan_imaging/Results/origin_CCA/out/Test_slide.csv", sep=''))

pdf(file=paste("~/documents/pancan_imaging/Results/origin_CCA/out/ROC_slide.pdf", sep=''),
    width=6,height=6)
for (i in 1:6){
  pos = paste(cancer[i], '_score', sep='')
  slide.sub = Test_slide[, c(pos, "True_label", "Prediction")]
  slide.sub$TL = ifelse(slide.sub["True_label"] == cancer[i], cancer[i], 'negative')
  slide.sub$PD = ifelse(slide.sub["Prediction"] == cancer[i], cancer[i], 'negative')
  lev = c('negative', cancer[i])

  answersa <- factor(slide.sub$TL)
  resultsa <- factor(slide.sub$PD)
  roca <- plot(roc(answersa, slide.sub[[pos]], levels=lev), print.auc = FALSE, col = color[i], add = (i!=1), labels = FALSE, tck = -0.02)
}
legend("bottomright", legend=c("CCRCC (AUROC=0.995)", "HNSCC (AUROC=0.993)", "LSCC (AUROC=0.949)", 
                               "LUAD (AUROC=0.967)", "PDA (AUROC=0.973)", "UCEC (AUROC=0.981)"),
       col=color, lwd=2)
dev.off()


pdf(file=paste("~/documents/pancan_imaging/Results/origin_CCA/out/ROC_tile.pdf", sep=''),
    width=6,height=6)
for (i in 1:6){
  pos = paste(cancer[i], '_score', sep='')
  tile.sub = Test_tile[, c(pos, "True_label", "Prediction")]
  tile.sub$TL = ifelse(tile.sub["True_label"] == cancer[i], cancer[i], 'negative')
  tile.sub$PD = ifelse(tile.sub["Prediction"] == cancer[i], cancer[i], 'negative')
  lev = c('negative', cancer[i])
  
  answersa <- factor(tile.sub$TL)
  resultsa <- factor(tile.sub$PD)
  roca <- plot(roc(answersa, tile.sub[[pos]], levels=lev), print.auc = FALSE, col = color[i], add = (i!=1), labels = FALSE, tck = -0.02)
}
legend("bottomright", legend=c("CCRCC (AUROC=0.963)", "HNSCC (AUROC=0.943)", "LSCC (AUROC=0.905)", 
                               "LUAD (AUROC=0.943)", "PDA (AUROC=0.933)", "UCEC (AUROC=0.952)"),
       col=color, lwd=2)
dev.off()




