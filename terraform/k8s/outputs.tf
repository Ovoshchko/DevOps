output "cluster_id" {
  description = "Managed Kubernetes cluster ID"
  value       = yandex_kubernetes_cluster.k8s-cluster.id
}

output "cluster_name" {
  description = "Managed Kubernetes cluster name"
  value       = yandex_kubernetes_cluster.k8s-cluster.name
}

output "node_group_id" {
  description = "Managed Kubernetes node group ID"
  value       = yandex_kubernetes_node_group.k8s-node-group.id
}

output "service_account_id" {
  description = "Service account used by the cluster and node group"
  value       = yandex_iam_service_account.k8s-sa.id
}
