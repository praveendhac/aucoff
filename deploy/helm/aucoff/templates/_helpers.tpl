{{- define "aucoff.labels" -}}
app.kubernetes.io/part-of: aucoff
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{- define "aucoff.podSecurityContext" -}}
runAsNonRoot: true
# Lets the non-root service user read mounted TLS keys (mode 0440).
fsGroup: 10001
seccompProfile:
  type: RuntimeDefault
{{- end -}}

{{- define "aucoff.containerSecurityContext" -}}
allowPrivilegeEscalation: false
readOnlyRootFilesystem: true
capabilities:
  drop: ["ALL"]
{{- end -}}
