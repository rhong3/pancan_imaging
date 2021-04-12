# Cancer type specific
# Calculate bootstraped CI of accuracy, AUROC, AUPRC and other statistical metrics. Gather them into a single file.
library(readxl)
library(caret)
library(pROC)
library(dplyr)
library(MLmetrics)
library(boot)
library(gmodels)

inlist = c('stage_10-10')
# Check previously calculated trials
previous=read.csv("~/Documents/pancan_imaging/Results/Statistics_stage.csv")
existed=paste(previous$Folder, previous$Type_number, sep='-')
# Find the new trials to be calculated
targets = inlist[which(!inlist %in% existed)]
OUTPUT = setNames(data.frame(matrix(ncol = 192, nrow = 0)), c("Folder", "Type_number"                    , "Slide_Multiclass_ROC.95.CI_lower"   ,    
                                                             "Slide_Multiclass_ROC"                   , "Slide_Multiclass_ROC.95.CI_upper"       , "Slide_stage0_ROC.95.CI_lower"          ,    
                                                             "Slide_stage0_ROC"                          , "Slide_stage0_ROC.95.CI_upper"              , "Slide_stage1_ROC.95.CI_lower" ,    
                                                             "Slide_stage1_ROC"                 , "Slide_stage1_ROC.95.CI_upper"     , "Slide_stage2_ROC.95.CI_lower"  ,    
                                                             "Slide_stage2_ROC"                  , "Slide_stage2_ROC.95.CI_upper"      , "Slide_stage3_ROC.95.CI_lower"         ,    
                                                             "Slide_stage3_ROC"                         , "Slide_stage3_ROC.95.CI_upper"             ,  "Slide_stage4_ROC.95.CI_lower"          ,    
                                                             "Slide_stage4_ROC"                          , "Slide_stage4_ROC.95.CI_upper" , "Slide_stage0_PRC.95.CI_lower"          ,    
                                                             "Slide_stage0_PRC"                          , "Slide_stage0_PRC.95.CI_upper"              , "Slide_stage1_PRC.95.CI_lower" ,    
                                                             "Slide_stage1_PRC"                 , "Slide_stage1_PRC.95.CI_upper"     , "Slide_stage2_PRC.95.CI_lower"  ,    
                                                             "Slide_stage2_PRC"                  , "Slide_stage2_PRC.95.CI_upper"      , "Slide_stage3_PRC.95.CI_lower"         ,    
                                                             "Slide_stage3_PRC"                         , "Slide_stage3_PRC.95.CI_upper"      , "Slide_stage4_PRC.95.CI_lower"         ,    
                                                             "Slide_stage4_PRC"                         , "Slide_stage4_PRC.95.CI_upper"       , "Slide_Accuracy"                     ,    
                                                             "Slide_Kappa"                            , "Slide_AccuracyLower"                    , "Slide_AccuracyUpper"                ,    
                                                             "Slide_AccuracyNull"                     , "Slide_AccuracyPValue"                   , "Slide_McnemarPValue"                , "Slide_stage0_Sensitivity"              ,    
                                                             "Slide_stage0_Specificity"                  , "Slide_stage0_Pos.Pred.Value"               , "Slide_stage0_Neg.Pred.Value"           ,    
                                                             "Slide_stage0_Precision"                    , "Slide_stage0_Recall"                       , "Slide_stage0_F1"                       ,    
                                                             "Slide_stage0_Prevalence"                   , "Slide_stage0_Detection.Rate"               , "Slide_stage0_Detection.Prevalence"     ,    
                                                             "Slide_stage0_Balanced.Accuracy"            ,    
                                                             "Slide_stage1_Sensitivity"         , "Slide_stage1_Specificity"         , "Slide_stage1_Pos.Pred.Value"  ,    
                                                             "Slide_stage1_Neg.Pred.Value"      , "Slide_stage1_Precision"           , "Slide_stage1_Recall"          ,    
                                                             "Slide_stage1_F1"                  , "Slide_stage1_Prevalence"          , "Slide_stage1_Detection.Rate"  ,    
                                                             "Slide_stage1_Detection.Prevalence", "Slide_stage1_Balanced.Accuracy"   ,  "Slide_stage2_Sensitivity"          , "Slide_stage2_Specificity"          , "Slide_stage2_Pos.Pred.Value"   ,    
                                                             "Slide_stage2_Neg.Pred.Value"       , "Slide_stage2_Precision"            , "Slide_stage2_Recall"           ,    
                                                             "Slide_stage2_F1"                   , "Slide_stage2_Prevalence"           , "Slide_stage2_Detection.Rate"   ,    
                                                             "Slide_stage2_Detection.Prevalence" , "Slide_stage2_Balanced.Accuracy"    , "Slide_stage3_Sensitivity"                 , "Slide_stage3_Specificity"             ,    
                                                             "Slide_stage3_Pos.Pred.Value"              , "Slide_stage3_Neg.Pred.Value"              , "Slide_stage3_Precision"               ,    
                                                             "Slide_stage3_Recall"                      , "Slide_stage3_F1"                          , "Slide_stage3_Prevalence"              ,    
                                                             "Slide_stage3_Detection.Rate"              , "Slide_stage3_Detection.Prevalence"        , "Slide_stage3_Balanced.Accuracy"       ,   "Slide_stage4_Sensitivity"          , "Slide_stage4_Specificity"          , "Slide_stage4_Pos.Pred.Value"   ,    
                                                             "Slide_stage4_Neg.Pred.Value"       , "Slide_stage4_Precision"            , "Slide_stage4_Recall"           ,    
                                                             "Slide_stage4_F1"                   , "Slide_stage4_Prevalence"           , "Slide_stage4_Detection.Rate"   ,    
                                                             "Slide_stage4_Detection.Prevalence" , "Slide_stage4_Balanced.Accuracy"    ,  
                                                             "Tile_Multiclass_ROC.95.CI_lower"      ,    
                                                             "Tile_Multiclass_ROC"                      , "Tile_Multiclass_ROC.95.CI_upper"          , "Tile_stage0_ROC.95.CI_lower"             ,    
                                                             "Tile_stage0_ROC"                             , "Tile_stage0_ROC.95.CI_upper"                 , "Tile_stage1_ROC.95.CI_lower"    ,    
                                                             "Tile_stage1_ROC"                    , "Tile_stage1_ROC.95.CI_upper"        , "Tile_stage2_ROC.95.CI_lower"     ,    
                                                             "Tile_stage2_ROC"                     , "Tile_stage2_ROC.95.CI_upper"         , "Tile_stage3_ROC.95.CI_lower"            ,    
                                                             "Tile_stage3_ROC"                            , "Tile_stage3_ROC.95.CI_upper"                , "Tile_stage4_ROC.95.CI_lower"    ,    
                                                             "Tile_stage4_ROC"                    , "Tile_stage4_ROC.95.CI_upper"        , "Tile_stage0_PRC.95.CI_lower"             ,    
                                                             "Tile_stage0_PRC"                             , "Tile_stage0_PRC.95.CI_upper"                 , "Tile_stage1_PRC.95.CI_lower"    ,    
                                                             "Tile_stage1_PRC"                   ,  "Tile_stage1_PRC.95.CI_upper"       ,  "Tile_stage2_PRC.95.CI_lower"    ,     
                                                             "Tile_stage2_PRC"                    ,  "Tile_stage2_PRC.95.CI_upper"        ,  "Tile_stage3_PRC.95.CI_lower"           ,     
                                                             "Tile_stage3_PRC"                           ,  "Tile_stage3_PRC.95.CI_upper"               , "Tile_stage4_PRC.95.CI_lower"    ,     
                                                             "Tile_stage4_PRC"                    ,  "Tile_stage4_PRC.95.CI_upper"        ,  "Tile_Accuracy"                       ,     
                                                             "Tile_Kappa"                              ,  "Tile_AccuracyLower"                      ,  "Tile_AccuracyUpper"                  ,     
                                                             "Tile_AccuracyNull"                       ,  "Tile_AccuracyPValue"                     ,  "Tile_McnemarPValue"                  ,     
                                                             "Tile_stage0_Sensitivity"                ,     
                                                             "Tile_stage0_Specificity"                    ,  "Tile_stage0_Pos.Pred.Value"                 ,  "Tile_stage0_Neg.Pred.Value"             ,     
                                                             "Tile_stage0_Precision"                      ,  "Tile_stage0_Recall"                         ,  "Tile_stage0_F1"                         ,     
                                                             "Tile_stage0_Prevalence"                     ,  "Tile_stage0_Detection.Rate"                 ,  "Tile_stage0_Detection.Prevalence"       ,     
                                                             "Tile_stage0_Balanced.Accuracy"              , "Tile_stage1_Sensitivity"           ,  "Tile_stage1_Specificity"           ,  "Tile_stage1_Pos.Pred.Value"    ,     
                                                             "Tile_stage1_Neg.Pred.Value"        ,  "Tile_stage1_Precision"             ,  "Tile_stage1_Recall"            ,     
                                                             "Tile_stage1_F1"                    ,  "Tile_stage1_Prevalence"            ,  "Tile_stage1_Detection.Rate"    ,     
                                                             "Tile_stage1_Detection.Prevalence"  ,  "Tile_stage1_Balanced.Accuracy"     ,   "Tile_stage2_Sensitivity"            ,  "Tile_stage2_Specificity"            ,  "Tile_stage2_Pos.Pred.Value"     ,     
                                                             "Tile_stage2_Neg.Pred.Value"         ,  "Tile_stage2_Precision"              ,  "Tile_stage2_Recall"             ,     
                                                             "Tile_stage2_F1"                     ,  "Tile_stage2_Prevalence"             ,  "Tile_stage2_Detection.Rate"     ,     
                                                             "Tile_stage2_Detection.Prevalence"   ,  "Tile_stage2_Balanced.Accuracy", "Tile_stage3_Sensitivity"                   ,  "Tile_stage3_Specificity"               ,     
                                                             "Tile_stage3_Pos.Pred.Value"                ,  "Tile_stage3_Neg.Pred.Value"                ,  "Tile_stage3_Precision"                 ,     
                                                             "Tile_stage3_Recall"                        ,  "Tile_stage3_F1"                            ,  "Tile_stage3_Prevalence"                ,     
                                                             "Tile_stage3_Detection.Rate"                ,  "Tile_stage3_Detection.Prevalence"          ,  "Tile_stage3_Balanced.Accuracy"         ,   "Tile_stage4_Sensitivity"            ,  "Tile_stage4_Specificity"            ,  "Tile_stage4_Pos.Pred.Value"     ,     
                                                             "Tile_stage4_Neg.Pred.Value"         ,  "Tile_stage4_Precision"              ,  "Tile_stage4_Recall"             ,     
                                                             "Tile_stage4_F1"                     ,  "Tile_stage4_Prevalence"             ,  "Tile_stage4_Detection.Rate"     ,     
                                                             "Tile_stage4_Detection.Prevalence"   ,  "Tile_stage4_Balanced.Accuracy"  
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
      for (m in 1:5){
        temmp = data.frame(t(CMP$byClass[m,]))
        colnames(temmp) = paste(gsub('-', '\\.', strsplit(rownames(CMP$byClass)[m], ': ')[[1]][2]), colnames(temmp), sep='_')
        dddf = cbind(dddf, temmp)
      }
      # multiclass ROC
      score = select(Test_slide, stage0_score,	stage1_score,	stage2_score,	stage3_score,	stage4_score)
      colnames(score) = c("stage0", "stage1", "stage2", "stage3", "stage4")
      roc =  multiclass.roc(answers, score)$auc
      rocls=list()
      for (q in 1:100){
        sampleddf = Test_slide[sample(nrow(Test_slide), round(nrow(Test_slide)*0.8)),]
        score = select(sampleddf, stage0_score,	stage1_score,	stage2_score,	stage3_score,	stage4_score)
        colnames(score) = c("stage0", "stage1", "stage2", "stage3", "stage4")
        answers <- factor(sampleddf$True_label)
        rocls[q] = multiclass.roc(answers, score)$auc
      }
      rocci = ci(as.numeric(rocls))
      mcroc = data.frame('Multiclass_ROC.95.CI_lower' = rocci[2], 'Multiclass_ROC' = roc, 'Multiclass_ROC.95.CI_upper' = rocci[3])
      
      rocccc = as.data.frame(matrix(0, ncol = 0, nrow = 1))
      prcccc = as.data.frame(matrix(0, ncol = 0, nrow = 1))
      
      #ROC and PRC
      for (w in 2:6){
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
      for (m in 1:5){
        Ttemmp = data.frame(t(CMT$byClass[m,]))
        colnames(Ttemmp) = paste(gsub('-', '\\.', strsplit(rownames(CMT$byClass)[m], ': ')[[1]][2]), colnames(Ttemmp), sep='_')
        Tdddf = cbind(Tdddf, Ttemmp)
      }
      
      # multiclass ROC
      Tscore = select(Test_tile, stage0_score,	stage1_score,	stage2_score,	stage3_score,	stage4_score)
      colnames(Tscore) = c("stage0", "stage1", "stage2", "stage3", "stage4")
      Troc =  multiclass.roc(answers, Tscore)$auc
      Trocls=list()
      for (q in 1:10){
        Tsampleddf = Test_tile[sample(nrow(Test_tile), round(nrow(Test_tile)*0.8)),]
        Tscore = select(Tsampleddf, stage0_score,	stage1_score,	stage2_score,	stage3_score,	stage4_score)
        colnames(Tscore) = c("stage0", "stage1", "stage2", "stage3", "stage4")
        Tanswers <- factor(Tsampleddf$True_label)
        Trocls[q] = multiclass.roc(Tanswers, Tscore)$auc
      }
      Trocci = ci(as.numeric(Trocls))
      Tmcroc = data.frame('Multiclass_ROC.95.CI_lower' = Trocci[2], 'Multiclass_ROC' = Troc, 'Multiclass_ROC.95.CI_upper' = Trocci[3])
      
      Trocccc = as.data.frame(matrix(0, ncol = 0, nrow = 1))
      Tprcccc = as.data.frame(matrix(0, ncol = 0, nrow = 1))
      #ROC and PRC
      for (w in 8:12){
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
write.csv(New_OUTPUT, file = "~/documents/pancan_imaging/Results/Statistics_stage.csv", row.names=FALSE)


