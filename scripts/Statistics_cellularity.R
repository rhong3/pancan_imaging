# Cancer type specific
# Calculate bootstraped CI of accuracy, AUROC, AUPRC and other statistical metrics. Gather them into a single file.
library(readxl)
library(caret)
library(pROC)
library(dplyr)
library(MLmetrics)
library(boot)
library(gmodels)

inlist = c('cellularity_CCA-6')
# Check previously calculated trials
previous=read.csv("~/Documents/pancan_imaging/Results/Statistics_cellularity.csv")
existed=paste(previous$Folder, previous$Type_number, sep='-')
# Find the new trials to be calculated
targets = inlist[which(!inlist %in% existed)]
OUTPUT = setNames(data.frame(matrix(ncol = 124, nrow = 0)), c("Folder", "Type_number"                    , "Slide_Multiclass_ROC.95.CI_lower"   ,    
                                                              "Slide_Multiclass_ROC"                   , "Slide_Multiclass_ROC.95.CI_upper"       , "Slide_0_79_ROC.95.CI_lower"          ,    
                                                              "Slide_0_79_ROC"                          , "Slide_0_79_ROC.95.CI_upper"              , "Slide_80_89_ROC.95.CI_lower" ,    
                                                              "Slide_80_89_ROC"                 , "Slide_80_89_ROC.95.CI_upper"     , "Slide_90_100_ROC.95.CI_lower"  ,    
                                                              "Slide_90_100_ROC"                  , "Slide_90_100_ROC.95.CI_upper"      , "Slide_0_79_PRC.95.CI_lower"          ,    
                                                              "Slide_0_79_PRC"                          , "Slide_0_79_PRC.95.CI_upper"              , "Slide_80_89_PRC.95.CI_lower" ,    
                                                              "Slide_80_89_PRC"                 , "Slide_80_89_PRC.95.CI_upper"     , "Slide_90_100_PRC.95.CI_lower"  ,    
                                                              "Slide_90_100_PRC"                  , "Slide_90_100_PRC.95.CI_upper"    , "Slide_Accuracy"                     ,    
                                                              "Slide_Kappa"                            , "Slide_AccuracyLower"                    , "Slide_AccuracyUpper"                ,    
                                                              "Slide_AccuracyNull"                     , "Slide_AccuracyPValue"                   , "Slide_McnemarPValue"                , "Slide_0_79_Sensitivity"              ,    
                                                              "Slide_0_79_Specificity"                  , "Slide_0_79_Pos.Pred.Value"               , "Slide_0_79_Neg.Pred.Value"           ,    
                                                              "Slide_0_79_Precision"                    , "Slide_0_79_Recall"                       , "Slide_0_79_F1"                       ,    
                                                              "Slide_0_79_Prevalence"                   , "Slide_0_79_Detection.Rate"               , "Slide_0_79_Detection.Prevalence"     ,    
                                                              "Slide_0_79_Balanced.Accuracy"            ,    
                                                              "Slide_80_89_Sensitivity"         , "Slide_80_89_Specificity"         , "Slide_80_89_Pos.Pred.Value"  ,    
                                                              "Slide_80_89_Neg.Pred.Value"      , "Slide_80_89_Precision"           , "Slide_80_89_Recall"          ,    
                                                              "Slide_80_89_F1"                  , "Slide_80_89_Prevalence"          , "Slide_80_89_Detection.Rate"  ,    
                                                              "Slide_80_89_Detection.Prevalence", "Slide_80_89_Balanced.Accuracy"   ,  "Slide_90_100_Sensitivity"          , "Slide_90_100_Specificity"          , "Slide_90_100_Pos.Pred.Value"   ,    
                                                              "Slide_90_100_Neg.Pred.Value"       , "Slide_90_100_Precision"            , "Slide_90_100_Recall"           ,    
                                                              "Slide_90_100_F1"                   , "Slide_90_100_Prevalence"           , "Slide_90_100_Detection.Rate"   ,    
                                                              "Slide_90_100_Detection.Prevalence" , "Slide_90_100_Balanced.Accuracy"    ,  
                                                              "Tile_Multiclass_ROC.95.CI_lower"      ,    
                                                              "Tile_Multiclass_ROC"                      , "Tile_Multiclass_ROC.95.CI_upper"          , "Tile_0_79_ROC.95.CI_lower"             ,    
                                                              "Tile_0_79_ROC"                             , "Tile_0_79_ROC.95.CI_upper"                 , "Tile_80_89_ROC.95.CI_lower"    ,    
                                                              "Tile_80_89_ROC"                    , "Tile_80_89_ROC.95.CI_upper"        , "Tile_90_100_ROC.95.CI_lower"     ,    
                                                              "Tile_90_100_ROC"                     , "Tile_90_100_ROC.95.CI_upper"         , "Tile_0_79_PRC.95.CI_lower"             ,    
                                                              "Tile_0_79_PRC"                             , "Tile_0_79_PRC.95.CI_upper"                 , "Tile_80_89_PRC.95.CI_lower"    ,    
                                                              "Tile_80_89_PRC"                   ,  "Tile_80_89_PRC.95.CI_upper"       ,  "Tile_90_100_PRC.95.CI_lower"    ,     
                                                              "Tile_90_100_PRC"                    ,  "Tile_90_100_PRC.95.CI_upper"        ,  "Tile_Accuracy"                       ,     
                                                              "Tile_Kappa"                              ,  "Tile_AccuracyLower"                      ,  "Tile_AccuracyUpper"                  ,     
                                                              "Tile_AccuracyNull"                       ,  "Tile_AccuracyPValue"                     ,  "Tile_McnemarPValue"                  ,     
                                                              "Tile_0_79_Sensitivity"                ,     
                                                              "Tile_0_79_Specificity"                    ,  "Tile_0_79_Pos.Pred.Value"                 ,  "Tile_0_79_Neg.Pred.Value"             ,     
                                                              "Tile_0_79_Precision"                      ,  "Tile_0_79_Recall"                         ,  "Tile_0_79_F1"                         ,     
                                                              "Tile_0_79_Prevalence"                     ,  "Tile_0_79_Detection.Rate"                 ,  "Tile_0_79_Detection.Prevalence"       ,     
                                                              "Tile_0_79_Balanced.Accuracy"              , "Tile_80_89_Sensitivity"           ,  "Tile_80_89_Specificity"           ,  "Tile_80_89_Pos.Pred.Value"    ,     
                                                              "Tile_80_89_Neg.Pred.Value"        ,  "Tile_80_89_Precision"             ,  "Tile_80_89_Recall"            ,     
                                                              "Tile_80_89_F1"                    ,  "Tile_80_89_Prevalence"            ,  "Tile_80_89_Detection.Rate"    ,     
                                                              "Tile_80_89_Detection.Prevalence"  ,  "Tile_80_89_Balanced.Accuracy"     ,   "Tile_90_100_Sensitivity"            ,  "Tile_90_100_Specificity"            ,  "Tile_90_100_Pos.Pred.Value"     ,     
                                                              "Tile_90_100_Neg.Pred.Value"         ,  "Tile_90_100_Precision"              ,  "Tile_90_100_Recall"             ,     
                                                              "Tile_90_100_F1"                     ,  "Tile_90_100_Prevalence"             ,  "Tile_90_100_Detection.Rate"     ,     
                                                              "Tile_90_100_Detection.Prevalence"   ,  "Tile_90_100_Balanced.Accuracy"
))


# # PRC function for bootstrap
# auprc = function(data, indices){
#   sampleddf = data[indices,]
#   prc = PRAUC(sampleddf$POS_score, factor(sampleddf$True_label))
#   return(prc)
# }

for (i in targets){
  tryCatch(
    {
      print(i)
      folder = strsplit(i, '-')[[1]][1]  #split replicated trials
      type_number = strsplit(i, '-')[[1]][2]
      Test_slide <- read.csv(paste("~/documents/pancan_imaging/Results/", folder, "/out/Test_slide.csv", sep=''))
      Test_tile <- read.csv(paste("~/documents/pancan_imaging/Results/", folder, "/out/Test_tile.csv", sep=''))
      
      # per Slide level
      answers <- factor(Test_slide$True_label)
      results <- factor(Test_slide$Prediction)
      # statistical metrics
      CMP = confusionMatrix(data=results, reference=answers)
      dddf = data.frame(t(CMP$overall))
      for (m in 1:3){
        temmp = data.frame(t(CMP$byClass[m,]))
        colnames(temmp) = paste(gsub('-', '\\.', strsplit(rownames(CMP$byClass)[m], ': ')[[1]][2]), colnames(temmp), sep='_')
        dddf = cbind(dddf, temmp)
      }
      # multiclass ROC
      score = select(Test_slide, X0_79_score,	X80_89_score,	X90_100_score)
      colnames(score) = c("0_79_score", "80_89_score", "90_100_score")
      roc =  multiclass.roc(answers, score)$auc
      rocls=list()
      for (q in 1:100){
        sampleddf = Test_slide[sample(nrow(Test_slide), round(nrow(Test_slide)*0.8)),]
        score = select(sampleddf, X0_79_score,	X80_89_score,	X90_100_score)
        colnames(score) = c("0_79_score", "80_89_score", "90_100_score")
        answers <- factor(sampleddf$True_label)
        rocls[q] = multiclass.roc(answers, score)$auc
      }
      rocci = ci(as.numeric(rocls))
      mcroc = data.frame('Multiclass_ROC.95.CI_lower' = rocci[2], 'Multiclass_ROC' = roc, 'Multiclass_ROC.95.CI_upper' = rocci[3])
      
      rocccc = as.data.frame(matrix(0, ncol = 0, nrow = 1))
      prcccc = as.data.frame(matrix(0, ncol = 0, nrow = 1))
      
      #ROC and PRC
      for (w in 2:4){
        cpTest_slide = Test_slide
        case=strsplit(colnames(cpTest_slide)[w], 'X')[[1]][2]
        case = gsub('\\.', '-', c(case))
        cpTest_slide$True_label = as.character(cpTest_slide$True_label)
        cpTest_slide$True_label[cpTest_slide$True_label != case] = "negative"
        cpTest_slide$True_label = as.factor(cpTest_slide$True_label)
        answers <- factor(cpTest_slide$True_label)
        
        #ROC
        roc =  roc(answers, cpTest_slide[,w], levels = c("negative", case))
        rocdf = t(data.frame(ci.auc(roc)))
        colnames(rocdf) = paste(gsub('-', '\\.', c(case)), c('ROC.95.CI_lower', 'ROC', 'ROC.95.CI_upper'), sep='_')
        rocccc = cbind(rocccc, rocdf)
        
        # PRC
        SprcR = PRAUC(cpTest_slide[,w], answers)
        Sprls = list()
        for (j in 1:100){
          sampleddf = cpTest_slide[sample(nrow(cpTest_slide), round(nrow(cpTest_slide)*0.95)),]
          Sprc = PRAUC(sampleddf[,w], factor(sampleddf$True_label))
          Sprls[j] = Sprc
        }
        Sprcci = ci(as.numeric(Sprls))
        Sprcdf = data.frame('PRC.95.CI_lower' = Sprcci[2], 'PRC' = SprcR, 'PRC.95.CI_upper' = Sprcci[3])
        colnames(Sprcdf) = paste(gsub('-', '\\.', c(case)), colnames(Sprcdf), sep='_')
        prcccc = cbind(prcccc, Sprcdf)
      }
      
      # Combine and add prefix
      soverall = cbind(mcroc, rocccc, prcccc, dddf)
      colnames(soverall) = paste('Slide', colnames(soverall), sep='_')
      
      
      
      # per tile level
      answers <- factor(Test_tile$True_label)
      results <- factor(Test_tile$Prediction)
      # statistical metrics
      CMT = confusionMatrix(data=results, reference=answers)
      Tdddf = data.frame(t(CMT$overall))
      for (m in 1:3){
        Ttemmp = data.frame(t(CMT$byClass[m,]))
        colnames(Ttemmp) = paste(gsub('-', '\\.', strsplit(rownames(CMT$byClass)[m], ': ')[[1]][2]), colnames(Ttemmp), sep='_')
        Tdddf = cbind(Tdddf, Ttemmp)
      }
      
      # multiclass ROC
      Tscore = select(Test_tile, X0_79_score,	X80_89_score,	X90_100_score)
      colnames(Tscore) = c("0_79_score", "80_89_score", "90_100_score")
      Troc =  multiclass.roc(answers, Tscore)$auc
      Trocls=list()
      for (q in 1:10){
        Tsampleddf = Test_tile[sample(nrow(Test_tile), round(nrow(Test_tile)*0.8)),]
        Tscore = select(Tsampleddf, X0_79_score,	X80_89_score,	X90_100_score)
        colnames(Tscore) = c("0_79_score", "80_89_score", "90_100_score")
        Tanswers <- factor(Tsampleddf$True_label)
        Trocls[q] = multiclass.roc(Tanswers, Tscore)$auc
      }
      Trocci = ci(as.numeric(Trocls))
      Tmcroc = data.frame('Multiclass_ROC.95.CI_lower' = Trocci[2], 'Multiclass_ROC' = Troc, 'Multiclass_ROC.95.CI_upper' = Trocci[3])
      
      Trocccc = as.data.frame(matrix(0, ncol = 0, nrow = 1))
      Tprcccc = as.data.frame(matrix(0, ncol = 0, nrow = 1))
      #ROC and PRC
      for (w in 8:10){
        cpTest_tile = Test_tile
        case=strsplit(colnames(cpTest_tile)[w], 'X')[[1]][2]
        case = gsub('\\.', '-', c(case))
        cpTest_tile$True_label = as.character(cpTest_tile$True_label)
        cpTest_tile$True_label[cpTest_tile$True_label != case] = "negative"
        cpTest_tile$True_label = as.factor(cpTest_tile$True_label)
        Tanswers <- factor(cpTest_tile$True_label)
        
        #ROC
        Troc =  roc(Tanswers, cpTest_tile[,w], levels = c("negative", case))
        Trocdf = t(data.frame(ci.auc(Troc)))
        colnames(Trocdf) = paste(gsub('-', '\\.', c(case)), c('ROC.95.CI_lower', 'ROC', 'ROC.95.CI_upper'), sep='_')
        Trocccc = cbind(Trocccc, Trocdf)
        
        # PRC
        TprcR = PRAUC(cpTest_tile[,w], Tanswers)
        Tprls = list()
        for (j in 1:10){
          sampleddf = cpTest_tile[sample(nrow(cpTest_tile), round(nrow(cpTest_tile)*0.95)),]
          Tprc = PRAUC(sampleddf[,w], factor(sampleddf$True_label))
          Tprls[j] = Tprc
        }
        Tprcci = ci(as.numeric(Tprls))
        Tprcdf = data.frame('PRC.95.CI_lower' = Tprcci[2], 'PRC' = TprcR, 'PRC.95.CI_upper' = Tprcci[3])
        colnames(Tprcdf) = paste(gsub('-', '\\.', c(case)), colnames(Tprcdf), sep='_')
        Tprcccc = cbind(Tprcccc, Tprcdf)
      }
      
      # Combine and add prefix
      Toverall = cbind(Tmcroc, Trocccc, Tprcccc, Tdddf)
      colnames(Toverall) = paste('Tile', colnames(Toverall), sep='_')
      
      # Key names
      keydf = data.frame("Folder" = folder, "Type_number" = type_number)
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
write.csv(New_OUTPUT, file = "~/documents/pancan_imaging/Results/Statistics_cellularity.csv", row.names=FALSE)


