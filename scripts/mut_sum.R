# Mutation Summary Table
co <- read_delim("Somatic_mutation_wxs/CO/AWG_data_freeze/Human__CPTAC_COAD__WUSM__Mutation__GAIIx__03_01_2017__BCM__Gene__GATK_Pipeline.cbt", 
                 "\t", escape_double = FALSE, trim_ws = TRUE)
mm = co$attrib_name
co = co[,-1]
row.names(co) = mm

pda <- read_delim("Somatic_mutation_wxs/PDA/AWG_data_freeze/Mutation_gene_level.cct", "\t", escape_double = FALSE, trim_ws = TRUE)
mm = pda$X1
pda = pda[, -1]
pda = data.frame(lapply(pda, function(x) {x = (x!='WT')}))
pda = data.frame(lapply(pda, as.numeric))
row.names(pda) = mm
colnames(pda) = gsub('\\.', '-', colnames(pda))

hnscc <- read_delim("Somatic_mutation_wxs/HNSCC/AWG_data_freeze/SomaticMutations_gene_level.cbt", 
                    "\t", escape_double = FALSE, trim_ws = TRUE)
mm = hnscc$idx
hnscc = hnscc[,-1]
row.names(hnscc) = mm

ucec <- read_delim("Somatic_mutation_wxs/EC/AWG_data_freeze/HS_CPTAC_UCEC_SomaticMutations_gene_level.cbt", 
                   "\t", escape_double = FALSE, trim_ws = TRUE)
mm = ucec$idx
ucec = ucec[,-1]
row.names(ucec) = mm



brca <- read_table2("Somatic_mutation_wxs/BR/AWG_data_freeze/prosp-brca-v5.3-any-somatic-mutation-freq-by-gene.gct")
lscc <- read_delim("Somatic_mutation_wxs/LSCC/AWG_data_freeze/lscc-v3.2-any-somatic-mutation-freq-by-gene.gct", 
                   "\t", escape_double = FALSE, trim_ws = TRUE)
luad <- read_delim("Somatic_mutation_wxs/LUAD/AWG_data_freeze/luad-v3.2-any-somatic-mutation-freq-by-gene.gct", 
                   "\t", escape_double = FALSE, trim_ws = TRUE)

ccrcc <- read_delim("Somatic_mutation_wxs/ccRCC/AWG_data_freeze/ccrcc.somatic.consensus.gdc.umichigan.wu.112918.maf", 
                    "\t", escape_double = FALSE, trim_ws = TRUE)
gbm <- read_delim("Somatic_mutation_wxs/GBM/AWG_data_freeze/somaticwrapper_all_cases_filtered_dnp_manual_review.v4.0.20200430.maf", 
                  "\t", escape_double = FALSE, trim_ws = TRUE)
ov <- read_delim("Somatic_mutation_wxs/OV/AWG_data_freeze/CPTAC2_Prospective_OV.v1.5.hg38.somatic.2019-01-19.maf", 
                 "\t", escape_double = FALSE, trim_ws = TRUE)



