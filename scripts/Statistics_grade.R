# Cancer type specific
# Calculate bootstraped CI of accuracy, AUROC, AUPRC and other statistical metrics. Gather them into a single file.
library(readxl)
library(caret)
library(pROC)
library(dplyr)
library(MLmetrics)
library(boot)
library(gmodels)

inlist = c('grade_CCA-6')
# Check previously calculated trials
previous=read.csv("~/Documents/pancan_imaging/Results/Statistics_grade.csv")
existed=paste(previous$Folder, previous$Type_number, sep='-')
# Find the new trials to be calculated
targets = inlist[which(!inlist %in% existed)]
OUTPUT = setNames(data.frame(matrix(ncol = 192, nrow = 0)), c("Folder", "Type_number"                    , "Slide_Multiclass_ROC.95.CI_lower"   ,    
                                                              "Slide_Multiclass_ROC"                   , "Slide_Multiclass_ROC.95.CI_upper"       , "Slide_grade0_ROC.95.CI_lower"          ,    
                                                              "Slide_grade0_ROC"                          , "Slide_grade0_ROC.95.CI_upper"              , "Slide_grade1_ROC.95.CI_lower" ,    
                                                              "Slide_grade1_ROC"                 , "Slide_grade1_ROC.95.CI_upper"     , "Slide_grade2_ROC.95.CI_lower"  ,    
                                                              "Slide_grade2_ROC"                  , "Slide_grade2_ROC.95.CI_upper"      , "Slide_grade3_ROC.95.CI_lower"         ,    
                                                              "Slide_grade3_ROC"                         , "Slide_grade3_ROC.95.CI_upper"             ,  "Slide_grade4_ROC.95.CI_lower"          ,    
                                                              "Slide_grade4_ROC"                          , "Slide_grade4_ROC.95.CI_upper" , "Slide_grade0_PRC.95.CI_lower"          ,    
                                                              "Slide_grade0_PRC"                          , "Slide_grade0_PRC.95.CI_upper"              , "Slide_grade1_PRC.95.CI_lower" ,    
                                                              "Slide_grade1_PRC"                 , "Slide_grade1_PRC.95.CI_upper"     , "Slide_grade2_PRC.95.CI_lower"  ,    
                                                              "Slide_grade2_PRC"                  , "Slide_grade2_PRC.95.CI_upper"      , "Slide_grade3_PRC.95.CI_lower"         ,    
                                                              "Slide_grade3_PRC"                         , "Slide_grade3_PRC.95.CI_upper"      , "Slide_grade4_PRC.95.CI_lower"         ,    
                                                              "Slide_grade4_PRC"                         , "Slide_grade4_PRC.95.CI_upper"       , "Slide_Accuracy"                     ,    
                                                              "Slide_Kappa"                            , "Slide_AccuracyLower"                    , "Slide_AccuracyUpper"                ,    
                                                              "Slide_AccuracyNull"                     , "Slide_AccuracyPValue"                   , "Slide_McnemarPValue"                , "Slide_grade0_Sensitivity"              ,    
                                                              "Slide_grade0_Specificity"                  , "Slide_grade0_Pos.Pred.Value"               , "Slide_grade0_Neg.Pred.Value"           ,    
                                                              "Slide_grade0_Precision"                    , "Slide_grade0_Recall"                       , "Slide_grade0_F1"                       ,    
                                                              "Slide_grade0_Prevalence"                   , "Slide_grade0_Detection.Rate"               , "Slide_grade0_Detection.Prevalence"     ,    
                                                              "Slide_grade0_Balanced.Accuracy"            ,    
                                                              "Slide_grade1_Sensitivity"         , "Slide_grade1_Specificity"         , "Slide_grade1_Pos.Pred.Value"  ,    
                                                              "Slide_grade1_Neg.Pred.Value"      , "Slide_grade1_Precision"           , "Slide_grade1_Recall"          ,    
                                                              "Slide_grade1_F1"                  , "Slide_grade1_Prevalence"          , "Slide_grade1_Detection.Rate"  ,    
                                                              "Slide_grade1_Detection.Prevalence", "Slide_grade1_Balanced.Accuracy"   ,  "Slide_grade2_Sensitivity"          , "Slide_grade2_Specificity"          , "Slide_grade2_Pos.Pred.Value"   ,    
                                                              "Slide_grade2_Neg.Pred.Value"       , "Slide_grade2_Precision"            , "Slide_grade2_Recall"           ,    
                                                              "Slide_grade2_F1"                   , "Slide_grade2_Prevalence"           , "Slide_grade2_Detection.Rate"   ,    
                                                              "Slide_grade2_Detection.Prevalence" , "Slide_grade2_Balanced.Accuracy"    , "Slide_grade3_Sensitivity"                 , "Slide_grade3_Specificity"             ,    
                                                              "Slide_grade3_Pos.Pred.Value"              , "Slide_grade3_Neg.Pred.Value"              , "Slide_grade3_Precision"               ,    
                                                              "Slide_grade3_Recall"                      , "Slide_grade3_F1"                          , "Slide_grade3_Prevalence"              ,    
                                                              "Slide_grade3_Detection.Rate"              , "Slide_grade3_Detection.Prevalence"        , "Slide_grade3_Balanced.Accuracy"       ,   "Slide_grade4_Sensitivity"          , "Slide_grade4_Specificity"          , "Slide_grade4_Pos.Pred.Value"   ,    
                                                              "Slide_grade4_Neg.Pred.Value"       , "Slide_grade4_Precision"            , "Slide_grade4_Recall"           ,    
                                                              "Slide_grade4_F1"                   , "Slide_grade4_Prevalence"           , "Slide_grade4_Detection.Rate"   ,    
                                                              "Slide_grade4_Detection.Prevalence" , "Slide_grade4_Balanced.Accuracy"    ,  
                                                              "Tile_Multiclass_ROC.95.CI_lower"      ,    
                                                              "Tile_Multiclass_ROC"                      , "Tile_Multiclass_ROC.95.CI_upper"          , "Tile_grade0_ROC.95.CI_lower"             ,    
                                                              "Tile_grade0_ROC"                             , "Tile_grade0_ROC.95.CI_upper"                 , "Tile_grade1_ROC.95.CI_lower"    ,    
                                                              "Tile_grade1_ROC"                    , "Tile_grade1_ROC.95.CI_upper"        , "Tile_grade2_ROC.95.CI_lower"     ,    
                                                              "Tile_grade2_ROC"                     , "Tile_grade2_ROC.95.CI_upper"         , "Tile_grade3_ROC.95.CI_lower"            ,    
                                                              "Tile_grade3_ROC"                            , "Tile_grade3_ROC.95.CI_upper"                , "Tile_grade4_ROC.95.CI_lower"    ,    
                                                              "Tile_grade4_ROC"                    , "Tile_grade4_ROC.95.CI_upper"        , "Tile_grade0_PRC.95.CI_lower"             ,    
                                                              "Tile_grade0_PRC"                             , "Tile_grade0_PRC.95.CI_upper"                 , "Tile_grade1_PRC.95.CI_lower"    ,    
                                                              "Tile_grade1_PRC"                   ,  "Tile_grade1_PRC.95.CI_upper"       ,  "Tile_grade2_PRC.95.CI_lower"    ,     
                                                              "Tile_grade2_PRC"                    ,  "Tile_grade2_PRC.95.CI_upper"        ,  "Tile_grade3_PRC.95.CI_lower"           ,     
                                                              "Tile_grade3_PRC"                           ,  "Tile_grade3_PRC.95.CI_upper"               , "Tile_grade4_PRC.95.CI_lower"    ,     
                                                              "Tile_grade4_PRC"                    ,  "Tile_grade4_PRC.95.CI_upper"        ,  "Tile_Accuracy"                       ,     
                                                              "Tile_Kappa"                              ,  "Tile_AccuracyLower"                      ,  "Tile_AccuracyUpper"                  ,     
                                                              "Tile_AccuracyNull"                       ,  "Tile_AccuracyPValue"                     ,  "Tile_McnemarPValue"                  ,     
                                                              "Tile_grade0_Sensitivity"                ,     
                                                              "Tile_grade0_Specificity"                    ,  "Tile_grade0_Pos.Pred.Value"                 ,  "Tile_grade0_Neg.Pred.Value"             ,     
                                                              "Tile_grade0_Precision"                      ,  "Tile_grade0_Recall"                         ,  "Tile_grade0_F1"                         ,     
                                                              "Tile_grade0_Prevalence"                     ,  "Tile_grade0_Detection.Rate"                 ,  "Tile_grade0_Detection.Prevalence"       ,     
                                                              "Tile_grade0_Balanced.Accuracy"              , "Tile_grade1_Sensitivity"           ,  "Tile_grade1_Specificity"           ,  "Tile_grade1_Pos.Pred.Value"    ,     
                                                              "Tile_grade1_Neg.Pred.Value"        ,  "Tile_grade1_Precision"             ,  "Tile_grade1_Recall"            ,     
                                                              "Tile_grade1_F1"                    ,  "Tile_grade1_Prevalence"            ,  "Tile_grade1_Detection.Rate"    ,     
                                                              "Tile_grade1_Detection.Prevalence"  ,  "Tile_grade1_Balanced.Accuracy"     ,   "Tile_grade2_Sensitivity"            ,  "Tile_grade2_Specificity"            ,  "Tile_grade2_Pos.Pred.Value"     ,     
                                                              "Tile_grade2_Neg.Pred.Value"         ,  "Tile_grade2_Precision"              ,  "Tile_grade2_Recall"             ,     
                                                              "Tile_grade2_F1"                     ,  "Tile_grade2_Prevalence"             ,  "Tile_grade2_Detection.Rate"     ,     
                                                              "Tile_grade2_Detection.Prevalence"   ,  "Tile_grade2_Balanced.Accuracy", "Tile_grade3_Sensitivity"                   ,  "Tile_grade3_Specificity"               ,     
                                                              "Tile_grade3_Pos.Pred.Value"                ,  "Tile_grade3_Neg.Pred.Value"                ,  "Tile_grade3_Precision"                 ,     
                                                              "Tile_grade3_Recall"                        ,  "Tile_grade3_F1"                            ,  "Tile_grade3_Prevalence"                ,     
                                                              "Tile_grade3_Detection.Rate"                ,  "Tile_grade3_Detection.Prevalence"          ,  "Tile_grade3_Balanced.Accuracy"         ,   "Tile_grade4_Sensitivity"            ,  "Tile_grade4_Specificity"            ,  "Tile_grade4_Pos.Pred.Value"     ,     
                                                              "Tile_grade4_Neg.Pred.Value"         ,  "Tile_grade4_Precision"              ,  "Tile_grade4_Recall"             ,     
                                                              "Tile_grade4_F1"                     ,  "Tile_grade4_Prevalence"             ,  "Tile_grade4_Detection.Rate"     ,     
                                                              "Tile_grade4_Detection.Prevalence"   ,  "Tile_grade4_Balanced.Accuracy"  
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
      score = select(Test_slide, grade0_score,	grade1_score,	grade2_score,	grade3_score,	grade4_score)
      colnames(score) = c("grade0", "grade1", "grade2", "grade3", "grade4")
      roc =  multiclass.roc(answers, score)$auc
      rocls=list()
      for (q in 1:100){
        sampleddf = Test_slide[sample(nrow(Test_slide), round(nrow(Test_slide)*0.8)),]
        score = select(sampleddf, grade0_score,	grade1_score,	grade2_score,	grade3_score,	grade4_score)
        colnames(score) = c("grade0", "grade1", "grade2", "grade3", "grade4")
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
      Tscore = select(Test_tile, grade0_score,	grade1_score,	grade2_score,	grade3_score,	grade4_score)
      colnames(Tscore) = c("grade0", "grade1", "grade2", "grade3", "grade4")
      Troc =  multiclass.roc(answers, Tscore)$auc
      Trocls=list()
      for (q in 1:10){
        Tsampleddf = Test_tile[sample(nrow(Test_tile), round(nrow(Test_tile)*0.8)),]
        Tscore = select(Tsampleddf, grade0_score,	grade1_score,	grade2_score,	grade3_score,	grade4_score)
        colnames(Tscore) = c("grade0", "grade1", "grade2", "grade3", "grade4")
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
write.csv(New_OUTPUT, file = "~/documents/pancan_imaging/Results/Statistics_grade.csv", row.names=FALSE)


