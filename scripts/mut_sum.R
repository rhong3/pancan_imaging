# Mutation Summary Table
library(readr)
library(data.table)
library(dplyr)
co <- read_delim("Somatic_mutation_wxs/CO/AWG_data_freeze/Human__CPTAC_COAD__WUSM__Mutation__GAIIx__03_01_2017__BCM__Gene__GATK_Pipeline.cbt", 
                 "\t", escape_double = FALSE, trim_ws = TRUE)
mm = co$attrib_name
co = co[,-1]
row.names(co) = mm
co.t = transpose(co)
rownames(co.t) <- colnames(co)
colnames(co.t) <- rownames(co)
co.t$Tumor = 'CO'
co.t <- co.t %>% select(Tumor, everything())

pda <- read_delim("Somatic_mutation_wxs/PDA/AWG_data_freeze/Mutation_gene_level.cct", "\t", escape_double = FALSE, trim_ws = TRUE)
mm = pda$X1
pda = pda[, -1]
pda = data.frame(lapply(pda, function(x) {x = (x!='WT')}))
pda = data.frame(lapply(pda, as.numeric))
row.names(pda) = mm
colnames(pda) = gsub('\\.', '-', colnames(pda))
pda.t = transpose(pda)
rownames(pda.t) <- colnames(pda)
colnames(pda.t) <- rownames(pda)
pda.t$Tumor = 'PDA'
pda.t <- pda.t %>% select(Tumor, everything())

hnscc <- read_delim("Somatic_mutation_wxs/HNSCC/AWG_data_freeze/SomaticMutations_gene_level.cbt", 
                    "\t", escape_double = FALSE, trim_ws = TRUE)
mm = hnscc$idx
hnscc = hnscc[,-1]
row.names(hnscc) = mm
hnscc.t = transpose(hnscc)
rownames(hnscc.t) <- colnames(hnscc)
colnames(hnscc.t) <- rownames(hnscc)
hnscc.t$Tumor = 'HNSCC'
hnscc.t <- hnscc.t %>% select(Tumor, everything())

ucec <- read_delim("Somatic_mutation_wxs/EC/AWG_data_freeze/HS_CPTAC_UCEC_SomaticMutations_gene_level.cbt", 
                   "\t", escape_double = FALSE, trim_ws = TRUE)
mm = ucec$idx
ucec = ucec[,-1]
row.names(ucec) = mm
row.names(ucec) = mm
ucec.t = transpose(ucec)
rownames(ucec.t) <- colnames(ucec)
colnames(ucec.t) <- rownames(ucec)
ucec.t$Tumor = 'UCEC'
ucec.t <- ucec.t %>% select(Tumor, everything())

brca <- read_delim("Somatic_mutation_wxs/BR/AWG_data_freeze/prosp-brca-v5.3-any-somatic-mutation-freq-by-gene.gct", 
                   "\t", escape_double = FALSE, trim_ws = TRUE)
brca = brca[-c(1:83), -c(2:6)]
brca = brca[!duplicated(brca$id),]
mm = brca$id
brca = data.frame(lapply(brca, function(x) {x = (x!=0)}))
brca = data.frame(lapply(brca, as.numeric))
brca = brca[, -1]
row.names(brca) = mm
colnames(brca) = gsub('X', '', colnames(brca))
brca.t = transpose(brca)
rownames(brca.t) <- colnames(brca)
colnames(brca.t) <- rownames(brca)
brca.t$Tumor = 'BRCA'
brca.t <- brca.t %>% select(Tumor, everything())

lscc <- read_delim("Somatic_mutation_wxs/LSCC/AWG_data_freeze/lscc-v3.2-any-somatic-mutation-freq-by-gene.gct", 
                   "\t", escape_double = FALSE, trim_ws = TRUE)
lscc = lscc[-c(1:80), -c(2:6)]
lscc = lscc[!duplicated(lscc$id),]
mm = lscc$id
lscc = data.frame(lapply(lscc, function(x) {x = (x!=0)}))
lscc = data.frame(lapply(lscc, as.numeric))
lscc = lscc[, -1]
row.names(lscc) = mm
lscc.t = transpose(lscc)
rownames(lscc.t) <- colnames(lscc)
colnames(lscc.t) <- rownames(lscc)
lscc.t$Tumor = 'LSCC'
lscc.t <- lscc.t %>% select(Tumor, everything())
row.names(lscc.t) = gsub('\\.', '-', row.names(lscc.t))

luad <- read_delim("Somatic_mutation_wxs/LUAD/AWG_data_freeze/luad-v3.2-any-somatic-mutation-freq-by-gene.gct", 
                   "\t", escape_double = FALSE, trim_ws = TRUE)
luad = luad[-c(1:68), -c(2:7)]
luad = luad[!duplicated(luad$id),]
mm = luad$id
luad = data.frame(lapply(luad, function(x) {x = (x!=0)}))
luad = data.frame(lapply(luad, as.numeric))
luad = luad[, -1]
row.names(luad) = mm
luad.t = transpose(luad)
rownames(luad.t) <- colnames(luad)
colnames(luad.t) <- rownames(luad)
luad.t$Tumor = 'LUAD'
luad.t <- luad.t %>% select(Tumor, everything())
row.names(luad.t) = gsub('\\.', '-', row.names(luad.t))


ccrcc <- read_delim("Somatic_mutation_wxs/ccRCC/AWG_data_freeze/ccrcc.somatic.consensus.gdc.umichigan.wu.112918.maf", 
                    "\t", escape_double = FALSE, trim_ws = TRUE)
ccrcc$Tumor_Sample_Barcode = gsub('_T', '', ccrcc$Tumor_Sample_Barcode)
samples = unique(ccrcc$Tumor_Sample_Barcode)

gbm <- read_delim("Somatic_mutation_wxs/GBM/AWG_data_freeze/somaticwrapper_all_cases_filtered_dnp_manual_review.v4.0.20200430.maf", 
                  "\t", escape_double = FALSE, trim_ws = TRUE)
ov <- read_delim("Somatic_mutation_wxs/OV/AWG_data_freeze/CPTAC2_Prospective_OV.v1.5.hg38.somatic.2019-01-19.maf", 
                 "\t", escape_double = FALSE, trim_ws = TRUE)



