# Read GCT file
# Read GCT file
library(NMF)
gct_data <- read.csv("tables/full.gct", header = TRUE)
gct_data <- as.matrix(gct_data[complete.cases(gct_data), ])
gct_data <- gct_data[rowSums(gct_data != 0) > 0, ]
nmf_model <- nmf(head(gct_data, n=length(gct_data/4)), rank= 2:15, nrun = 5, .opt="v")
pdf()
cluster_assignments <- consensusmap(nmf_model)
dev.off()
# Determine optimal number of clusters
coph <- cophenetic(cluster_assignments)
optimal_k <- which.max(coph)

# Extract the final clustering solution
cluster_assign <- cluster_assignments[[optimal_k]]

# Explore clustering results
table(cluster_assign)