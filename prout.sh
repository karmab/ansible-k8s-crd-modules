oc get configmap -n kube-system kube-controller-manager -o jsonpath="{ .metadata.annotations.control-plane\.alpha\.kubernetes\.io/leader}"
oc get configmap -n kube-system kube-controller-manager -o jsonpath="{ .metadata.annotations.control-plane\.alpha\.kubernetes\.io/leader['holderIdentity']}"
#oc get configmap -n kube-system kube-controller-manager -o 'go-template={{ index .metadata.annotations.control\-plane\.alpha\.kubernetes\.io/leader }}'
