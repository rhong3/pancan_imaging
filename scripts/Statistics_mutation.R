# Cancer type specific
# Calculate bootstraped CI of accuracy, AUROC, AUPRC and other statistical metrics. Gather them into a single file.
library(readxl)
library(caret)
library(pROC)
library(dplyr)
library(MLmetrics)
library(boot)
library(gmodels)

inlist = c('MAP3K1_CCA-MAP3K1')
# Check previously calculated trials
previous=read.csv("~/Documents/pancan_imaging/Results/Statistics_mutation.csv")
existed=paste(previous$Folder, previous$Gene, previous$Type_number, sep='-')
# Find the new trials to be calculated
targets = inlist[which(!inlist %in% existed)]
OUTPUT = setNames(data.frame(matrix(ncol = 51, nrow = 0)), c("Folder", "Gene", "Type_number", "Slide_ROC.95.CI_lower", "Slide_ROC",                 
                                                             "Slide_ROC.95.CI_upper",      "Slide_PRC.95.CI_lower",      "Slide_PRC",                  "Slide_PRC.95%CI_upper",      "Slide_Accuracy",            
                                                             "Slide_Kappa",                "Slide_AccuracyLower",        "Slide_AccuracyUpper",        "Slide_AccuracyNull",         "Slide_AccuracyPValue",      
                                                             "Slide_McnemarPValue",        "Slide_Sensitivity",          "Slide_Specificity",          "Slide_Pos.Pred.Value",       "Slide_Neg.Pred.Value",      
                                                             "Slide_Precision",            "Slide_Recall",               "Slide_F1",                   "Slide_Prevalence",           "Slide_Detection.Rate",      
                                                             "Slide_Detection.Prevalence", "Slide_Balanced.Accuracy",    "Tile_ROC.95.CI_lower",         "Tile_ROC",                     "Tile_ROC.95%CI_upper",        
                                                             "Tile_PRC.95.CI_lower",         "Tile_PRC",                     "Tile_PRC.95.CI_upper",         "Tile_Accuracy",                "Tile_Kappa",                  
                                                             "Tile_AccuracyLower",           "Tile_AccuracyUpper",           "Tile_AccuracyNull",            "Tile_AccuracyPValue",          "Tile_McnemarPValue",          
                                                             "Tile_Sensitivity",             "Tile_Specificity",             "Tile_Pos.Pred.Value",          "Tile_Neg.Pred.Value",          "Tile_Precision",              
                                                             "Tile_Recall",                  "Tile_F1",                      "Tile_Prevalence",              "Tile_Detection.Rate",          "Tile_Detection.Prevalence",   
                                                             "Tile_Balanced.Accuracy"))

# # PRC function for bootstrap
# auprc = function(data, indices){
#   sampleddf = data[indices,]
#   prc = PRAUC(sampleddf$POS_score, factor(sampleddf$True_label))
#   return(prc)
# }

for (i in targets){
  tryCatch(
    {
      pos = strsplit(i, '-')[[1]][2]  #get positive case name
      print(i)
      folder = strsplit(i, '-')[[1]][1]  #split replicated trials

      Test_slide <- read.csv(paste("~/documents/pancan_imaging/Results/", folder, "/out/Test_slide.csv", sep=''))
      Test_tile <- read.csv(paste("~/documents/pancan_imaging/Results/", folder, "/out/Test_tile.csv", sep=''))
      type_number <- nrow(unique(Test_slide['Tumor']))
      # per Slide level
      answers <- factor(Test_slide$True_label)
      results <- factor(Test_slide$Prediction)
      # statistical metrics
      CMP = confusionMatrix(data=results, reference=answers, positive = pos)
      # ROC
      roc =  roc(answers, Test_slide$POS_score, levels=c('negative', pos))
      rocdf = t(data.frame(ci.auc(roc)))
      colnames(rocdf) = c('ROC.95.CI_lower', 'ROC', 'ROC.95.CI_upper')
      # PRC
      SprcR = PRAUC(Test_slide$POS_score, factor(Test_slide$True_label))
      Sprls = list()
      for (j in 1:5){
        sampleddf = Test_slide[sample(nrow(Test_slide), round(nrow(Test_slide)*0.9)),]
        Sprc = PRAUC(sampleddf$POS_score, factor(sampleddf$True_label))
        Sprls[j] = Sprc
      }
      Sprcci = ci(as.numeric(Sprls))
      Sprcdf = data.frame('PRC.95.CI_lower' = Sprcci[2], 'PRC' = SprcR, 'PRC.95.CI_upper' = Sprcci[3])
      # Combine and add prefix
      soverall = cbind(rocdf, Sprcdf, data.frame(t(CMP$overall)), data.frame(t(CMP$byClass)))
      colnames(soverall) = paste('Slide', colnames(soverall), sep='_')
      
      # per tile level
      Tanswers <- factor(Test_tile$True_label)
      Tresults <- factor(Test_tile$Prediction)
      # statistical metrics
      CMT = confusionMatrix(data=Tresults, reference=Tanswers, positive = pos)
      # ROC
      Troc =  roc(Tanswers, Test_tile$POS_score, levels=c('negative', pos))
      Trocdf = t(data.frame(ci.auc(Troc)))
      colnames(Trocdf) = c('ROC.95.CI_lower', 'ROC', 'ROC.95.CI_upper')
      # PRC
      prcR = PRAUC(Test_tile$POS_score, factor(Test_tile$True_label))
      prls = list()
      for (j in 1:10){
        sampleddf = Test_tile[sample(nrow(Test_tile), round(nrow(Test_tile)*0.9)),]
        prc = PRAUC(sampleddf$POS_score, factor(sampleddf$True_label))
        prls[j] = prc
      }
      Tprcci = ci(as.numeric(prls))
      Tprcdf = data.frame('PRC.95.CI_lower' = Tprcci[2], 'PRC' = prcR, 'PRC.95.CI_upper' = Tprcci[3])
      # Combine and add prefix
      Toverall = cbind(Trocdf, Tprcdf, data.frame(t(CMT$overall)), data.frame(t(CMT$byClass)))
      colnames(Toverall) = paste('Tile', colnames(Toverall), sep='_')
      # Key names
      keydf = data.frame("Folder" = folder, "Gene" = pos, "Type_number" = type_number)
      # combine all df and reset row name
      tempdf = cbind(keydf, soverall, Toverall)
      rownames(tempdf) <- NULL
      OUTPUT = rbind(OUTPUT, tempdf)
    },
    error = function(error_message){
      message(error_message)
      message(i)
      return(NA)
    }
  )  
}

# Bind old with new; sort; save
New_OUTPUT = rbind(previous, OUTPUT)
New_OUTPUT = New_OUTPUT[order(New_OUTPUT$Folder, New_OUTPUT$Type_number),]
write.csv(New_OUTPUT, file = "~/documents/pancan_imaging/Results/Statistics_mutation.csv", row.names=FALSE)


