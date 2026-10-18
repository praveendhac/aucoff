{{- define "identity.labels" -}}
app.kubernetes.io/part-of: aucoff
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}
