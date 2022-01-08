# Cancer type specific
# Calculate bootstraped CI of accuracy, AUROC, AUPRC and other statistical metrics. Gather them into a single file.
library(readxl)
library(caret)
library(pROC)
library(dplyr)
library(MLmetrics)
library(boot)
library(gmodels)

inlist = c('origin_CCA-6')
# Check previously calculated trials
previous=read.csv("~/Documents/pancan_imaging/Results/Statistics_origin.csv")
existed=paste(previous$Folder, previous$Type_number, sep='-')
# Find the new trials to be calculated
targets = inlist[which(!inlist %in% existed)]
OUTPUT = setNames(data.frame(matrix(ncol = 226, nrow = 0)), c("Folder", "Type_number"                    , "Slide_Multiclass_ROC.95.CI_lower"   ,    
                                                              "Slide_Multiclass_ROC"                   , "Slide_Multiclass_ROC.95.CI_upper"       , "Slide_CCRCC_ROC.95.CI_lower"          ,    
                                                              "Slide_CCRCC_ROC"                          , "Slide_CCRCC_ROC.95.CI_upper"              , "Slide_HNSCC_ROC.95.CI_lower" ,    
                                                              "Slide_HNSCC_ROC"                 , "Slide_HNSCC_ROC.95.CI_upper"     , "Slide_LSCC_ROC.95.CI_lower"  ,    
                                                              "Slide_LSCC_ROC"                  , "Slide_LSCC_ROC.95.CI_upper"      , "Slide_LUAD_ROC.95.CI_lower"         ,    
                                                              "Slide_LUAD_ROC"                         , "Slide_LUAD_ROC.95.CI_upper"             ,  "Slide_PDA_ROC.95.CI_lower"          ,    
                                                              "Slide_PDA_ROC"                          , "Slide_PDA_ROC.95.CI_upper" , "Slide_UCEC_ROC.95.CI_lower" ,    
                                                              "Slide_UCEC_ROC"                 , "Slide_UCEC_ROC.95.CI_upper"     ,"Slide_CCRCC_PRC.95.CI_lower"          ,    
                                                              "Slide_CCRCC_PRC"                          , "Slide_CCRCC_PRC.95.CI_upper"              , "Slide_HNSCC_PRC.95.CI_lower" ,    
                                                              "Slide_HNSCC_PRC"                 , "Slide_HNSCC_PRC.95.CI_upper"     , "Slide_LSCC_PRC.95.CI_lower"  ,    
                                                              "Slide_LSCC_PRC"                  , "Slide_LSCC_PRC.95.CI_upper"      , "Slide_LUAD_PRC.95.CI_lower"         ,    
                                                              "Slide_LUAD_PRC"                         , "Slide_LUAD_PRC.95.CI_upper"      , "Slide_PDA_PRC.95.CI_lower"         ,    
                                                              "Slide_PDA_PRC"                         , "Slide_PDA_PRC.95.CI_upper"       , "Slide_UCEC_PRC.95.CI_lower" ,    
                                                              "Slide_UCEC_PRC"                 , "Slide_UCEC_PRC.95.CI_upper"     ,"Slide_Accuracy"                     ,    
                                                              "Slide_Kappa"                            , "Slide_AccuracyLower"                    , "Slide_AccuracyUpper"                ,    
                                                              "Slide_AccuracyNull"                     , "Slide_AccuracyPValue"                   , "Slide_McnemarPValue"                , "Slide_CCRCC_Sensitivity"              ,    
                                                              "Slide_CCRCC_Specificity"                  , "Slide_CCRCC_Pos.Pred.Value"               , "Slide_CCRCC_Neg.Pred.Value"           ,    
                                                              "Slide_CCRCC_Precision"                    , "Slide_CCRCC_Recall"                       , "Slide_CCRCC_F1"                       ,    
                                                              "Slide_CCRCC_Prevalence"                   , "Slide_CCRCC_Detection.Rate"               , "Slide_CCRCC_Detection.Prevalence"     ,    
                                                              "Slide_CCRCC_Balanced.Accuracy"            ,    
                                                              "Slide_HNSCC_Sensitivity"         , "Slide_HNSCC_Specificity"         , "Slide_HNSCC_Pos.Pred.Value"  ,    
                                                              "Slide_HNSCC_Neg.Pred.Value"      , "Slide_HNSCC_Precision"           , "Slide_HNSCC_Recall"          ,    
                                                              "Slide_HNSCC_F1"                  , "Slide_HNSCC_Prevalence"          , "Slide_HNSCC_Detection.Rate"  ,    
                                                              "Slide_HNSCC_Detection.Prevalence", "Slide_HNSCC_Balanced.Accuracy"   ,  "Slide_LSCC_Sensitivity"          , "Slide_LSCC_Specificity"          , "Slide_LSCC_Pos.Pred.Value"   ,    
                                                              "Slide_LSCC_Neg.Pred.Value"       , "Slide_LSCC_Precision"            , "Slide_LSCC_Recall"           ,    
                                                              "Slide_LSCC_F1"                   , "Slide_LSCC_Prevalence"           , "Slide_LSCC_Detection.Rate"   ,    
                                                              "Slide_LSCC_Detection.Prevalence" , "Slide_LSCC_Balanced.Accuracy"    , "Slide_LUAD_Sensitivity"                 , "Slide_LUAD_Specificity"             ,    
                                                              "Slide_LUAD_Pos.Pred.Value"              , "Slide_LUAD_Neg.Pred.Value"              , "Slide_LUAD_Precision"               ,    
                                                              "Slide_LUAD_Recall"                      , "Slide_LUAD_F1"                          , "Slide_LUAD_Prevalence"              ,    
                                                              "Slide_LUAD_Detection.Rate"              , "Slide_LUAD_Detection.Prevalence"        , "Slide_LUAD_Balanced.Accuracy"       ,   "Slide_PDA_Sensitivity"          , "Slide_PDA_Specificity"          , "Slide_PDA_Pos.Pred.Value"   ,    
                                                              "Slide_PDA_Neg.Pred.Value"       , "Slide_PDA_Precision"            , "Slide_PDA_Recall"           ,    
                                                              "Slide_PDA_F1"                   , "Slide_PDA_Prevalence"           , "Slide_PDA_Detection.Rate"   ,    
                                                              "Slide_PDA_Detection.Prevalence" , "Slide_PDA_Balanced.Accuracy"    ,  
                                                              "Slide_UCEC_Sensitivity"          , "Slide_UCEC_Specificity"          , "Slide_UCEC_Pos.Pred.Value"   ,    
                                                              "Slide_UCEC_Neg.Pred.Value"       , "Slide_UCEC_Precision"            , "Slide_UCEC_Recall"           ,    
                                                              "Slide_UCEC_F1"                   , "Slide_UCEC_Prevalence"           , "Slide_UCEC_Detection.Rate"   ,    
                                                              "Slide_UCEC_Detection.Prevalence" , "Slide_UCEC_Balanced.Accuracy"    ,  
                                                              "Tile_Multiclass_ROC.95.CI_lower"      ,    
                                                              "Tile_Multiclass_ROC"                      , "Tile_Multiclass_ROC.95.CI_upper"          , "Tile_CCRCC_ROC.95.CI_lower"             ,    
                                                              "Tile_CCRCC_ROC"                             , "Tile_CCRCC_ROC.95.CI_upper"                 , "Tile_HNSCC_ROC.95.CI_lower"    ,    
                                                              "Tile_HNSCC_ROC"                    , "Tile_HNSCC_ROC.95.CI_upper"        , "Tile_LSCC_ROC.95.CI_lower"     ,    
                                                              "Tile_LSCC_ROC"                     , "Tile_LSCC_ROC.95.CI_upper"         , "Tile_LUAD_ROC.95.CI_lower"            ,    
                                                              "Tile_LUAD_ROC"                            , "Tile_LUAD_ROC.95.CI_upper"                , "Tile_PDA_ROC.95.CI_lower"    ,    
                                                              "Tile_PDA_ROC"                    , "Tile_PDA_ROC.95.CI_upper"        , 
                                                              "Tile_UCEC_ROC.95.CI_lower"             ,    
                                                              "Tile_UCEC_ROC"                             , "Tile_UCEC_ROC.95.CI_upper"                 ,"Tile_CCRCC_PRC.95.CI_lower"             ,    
                                                              "Tile_CCRCC_PRC"                             , "Tile_CCRCC_PRC.95.CI_upper"                 , "Tile_HNSCC_PRC.95.CI_lower"    ,    
                                                              "Tile_HNSCC_PRC"                   ,  "Tile_HNSCC_PRC.95.CI_upper"       ,  "Tile_LSCC_PRC.95.CI_lower"    ,     
                                                              "Tile_LSCC_PRC"                    ,  "Tile_LSCC_PRC.95.CI_upper"        ,  "Tile_LUAD_PRC.95.CI_lower"           ,     
                                                              "Tile_LUAD_PRC"                           ,  "Tile_LUAD_PRC.95.CI_upper"               , "Tile_PDA_PRC.95.CI_lower"    ,     
                                                              "Tile_PDA_PRC"                    ,  "Tile_PDA_PRC.95.CI_upper"        ,  
                                                              "Tile_UCEC_PRC.95.CI_lower"    ,    
                                                              "Tile_UCEC_PRC"                   ,  "Tile_UCEC_PRC.95.CI_upper"       ,"Tile_Accuracy"                       ,     
                                                              "Tile_Kappa"                              ,  "Tile_AccuracyLower"                      ,  "Tile_AccuracyUpper"                  ,     
                                                              "Tile_AccuracyNull"                       ,  "Tile_AccuracyPValue"                     ,  "Tile_McnemarPValue"                  ,     
                                                              "Tile_CCRCC_Sensitivity"                ,     
                                                              "Tile_CCRCC_Specificity"                    ,  "Tile_CCRCC_Pos.Pred.Value"                 ,  "Tile_CCRCC_Neg.Pred.Value"             ,     
                                                              "Tile_CCRCC_Precision"                      ,  "Tile_CCRCC_Recall"                         ,  "Tile_CCRCC_F1"                         ,     
                                                              "Tile_CCRCC_Prevalence"                     ,  "Tile_CCRCC_Detection.Rate"                 ,  "Tile_CCRCC_Detection.Prevalence"       ,     
                                                              "Tile_CCRCC_Balanced.Accuracy"              , "Tile_HNSCC_Sensitivity"           ,  "Tile_HNSCC_Specificity"           ,  "Tile_HNSCC_Pos.Pred.Value"    ,     
                                                              "Tile_HNSCC_Neg.Pred.Value"        ,  "Tile_HNSCC_Precision"             ,  "Tile_HNSCC_Recall"            ,     
                                                              "Tile_HNSCC_F1"                    ,  "Tile_HNSCC_Prevalence"            ,  "Tile_HNSCC_Detection.Rate"    ,     
                                                              "Tile_HNSCC_Detection.Prevalence"  ,  "Tile_HNSCC_Balanced.Accuracy"     ,   "Tile_LSCC_Sensitivity"            ,  "Tile_LSCC_Specificity"            ,  "Tile_LSCC_Pos.Pred.Value"     ,     
                                                              "Tile_LSCC_Neg.Pred.Value"         ,  "Tile_LSCC_Precision"              ,  "Tile_LSCC_Recall"             ,     
                                                              "Tile_LSCC_F1"                     ,  "Tile_LSCC_Prevalence"             ,  "Tile_LSCC_Detection.Rate"     ,     
                                                              "Tile_LSCC_Detection.Prevalence"   ,  "Tile_LSCC_Balanced.Accuracy", "Tile_LUAD_Sensitivity"                   ,  "Tile_LUAD_Specificity"               ,     
                                                              "Tile_LUAD_Pos.Pred.Value"                ,  "Tile_LUAD_Neg.Pred.Value"                ,  "Tile_LUAD_Precision"                 ,     
                                                              "Tile_LUAD_Recall"                        ,  "Tile_LUAD_F1"                            ,  "Tile_LUAD_Prevalence"                ,     
                                                              "Tile_LUAD_Detection.Rate"                ,  "Tile_LUAD_Detection.Prevalence"          ,  "Tile_LUAD_Balanced.Accuracy"         ,   "Tile_PDA_Sensitivity"            ,  "Tile_PDA_Specificity"            ,  "Tile_PDA_Pos.Pred.Value"     ,     
                                                              "Tile_PDA_Neg.Pred.Value"         ,  "Tile_PDA_Precision"              ,  "Tile_PDA_Recall"             ,     
                                                              "Tile_PDA_F1"                     ,  "Tile_PDA_Prevalence"             ,  "Tile_PDA_Detection.Rate"     ,     
                                                              "Tile_PDA_Detection.Prevalence"   ,  "Tile_PDA_Balanced.Accuracy",  "Tile_UCEC_Sensitivity"           ,  "Tile_UCEC_Specificity"           ,  "Tile_HNSCC_Pos.Pred.Value"    ,     
                                                              "Tile_UCEC_Neg.Pred.Value"        ,  "Tile_UCEC_Precision"             ,  "Tile_UCEC_Recall"            ,     
                                                              "Tile_UCEC_F1"                    ,  "Tile_UCEC_Prevalence"            ,  "Tile_UCEC_Detection.Rate"    ,     
                                                              "Tile_UCEC_Detection.Prevalence"  ,  "Tile_UCEC_Balanced.Accuracy"     
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
      Test_slide = Test_slide[, !names(Test_slide) %in% c("BRCA_score", "OV_score", "CO_score", "GBM_score")]
      Test_tile <- read.csv(paste("~/documents/pancan_imaging/Results/", folder, "/out/Test_tile.csv", sep=''))
      Test_tile = Test_tile[, !names(Test_tile) %in%c("BRCA_score", "OV_score", "CO_score", "GBM_score")]
      
      # per Slide level
      answers <- factor(Test_slide$True_label)
      results <- factor(Test_slide$Prediction)
      # statistical metrics
      CMP = confusionMatrix(data=results, reference=answers)
      dddf = data.frame(t(CMP$overall))
      for (m in 1:6){
        temmp = data.frame(t(CMP$byClass[m,]))
        colnames(temmp) = paste(gsub('-', '\\.', strsplit(rownames(CMP$byClass)[m], ': ')[[1]][2]), colnames(temmp), sep='_')
        dddf = cbind(dddf, temmp)
      }
      # multiclass ROC
      score = select(Test_slide, CCRCC_score,	HNSCC_score,	LSCC_score,	LUAD_score,	PDA_score, UCEC_score)
      colnames(score) = c("CCRCC", "HNSCC", "LSCC", "LUAD", "PDA", "UCEC")
      roc =  multiclass.roc(answers, score)$auc
      rocls=list()
      for (q in 1:100){
        sampleddf = Test_slide[sample(nrow(Test_slide), round(nrow(Test_slide)*0.8)),]
        score = select(sampleddf, CCRCC_score,	HNSCC_score,	LSCC_score,	LUAD_score,	PDA_score, UCEC_score)
        colnames(score) = c("CCRCC", "HNSCC", "LSCC", "LUAD", "PDA", "UCEC")
        answers <- factor(sampleddf$True_label)
        rocls[q] = multiclass.roc(answers, score)$auc
      }
      rocci = ci(as.numeric(rocls))
      mcroc = data.frame('Multiclass_ROC.95.CI_lower' = rocci[2], 'Multiclass_ROC' = roc, 'Multiclass_ROC.95.CI_upper' = rocci[3])
      
      rocccc = as.data.frame(matrix(0, ncol = 0, nrow = 1))
      prcccc = as.data.frame(matrix(0, ncol = 0, nrow = 1))
      
      #ROC and PRC
      for (w in 2:7){
        cpTest_slide = Test_slide
        case=strsplit(colnames(cpTest_slide)[w], '_')[[1]][1]
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
      for (m in 1:6){
        Ttemmp = data.frame(t(CMT$byClass[m,]))
        colnames(Ttemmp) = paste(gsub('-', '\\.', strsplit(rownames(CMT$byClass)[m], ': ')[[1]][2]), colnames(Ttemmp), sep='_')
        Tdddf = cbind(Tdddf, Ttemmp)
      }
      
      # multiclass ROC
      Tscore = select(Test_tile, CCRCC_score,	HNSCC_score,	LSCC_score,	LUAD_score,	PDA_score, UCEC_score)
      colnames(Tscore) = c("CCRCC", "HNSCC", "LSCC", "LUAD", "PDA", "UCEC")
      Troc =  multiclass.roc(answers, Tscore)$auc
      Trocls=list()
      for (q in 1:10){
        Tsampleddf = Test_tile[sample(nrow(Test_tile), round(nrow(Test_tile)*0.8)),]
        Tscore = select(Tsampleddf, CCRCC_score,	HNSCC_score,	LSCC_score,	LUAD_score,	PDA_score, UCEC_score)
        colnames(Tscore) = c("CCRCC", "HNSCC", "LSCC", "LUAD", "PDA", "UCEC")
        Tanswers <- factor(Tsampleddf$True_label)
        Trocls[q] = multiclass.roc(Tanswers, Tscore)$auc
      }
      Trocci = ci(as.numeric(Trocls))
      Tmcroc = data.frame('Multiclass_ROC.95.CI_lower' = Trocci[2], 'Multiclass_ROC' = Troc, 'Multiclass_ROC.95.CI_upper' = Trocci[3])
      
      Trocccc = as.data.frame(matrix(0, ncol = 0, nrow = 1))
      Tprcccc = as.data.frame(matrix(0, ncol = 0, nrow = 1))
      #ROC and PRC
      for (w in 8:13){
        cpTest_tile = Test_tile
        case=strsplit(colnames(cpTest_tile)[w], '_')[[1]][1]
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
write.csv(New_OUTPUT, file = "~/documents/pancan_imaging/Results/Statistics_origin.csv", row.names=FALSE)


