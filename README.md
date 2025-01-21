# OAI RAN DU (Distributed Unit) Operator (k8s)
[![CharmHub Badge](https://charmhub.io/oai-ran-du-k8s/badge.svg)](https://charmhub.io/oai-ran-du-k8s)

A Charmed Operator for the OAI RAN Distributed Unit (DU) for K8s.

## Pre-requisites

A Kubernetes cluster with the Multus addon enabled.

## Usage

Enable the Multus addon on MicroK8s.

```bash
sudo microk8s addons repo add community https://github.com/canonical/microk8s-community-addons --reference feat/strict-fix-multus
sudo microk8s enable multus
```

Deploy the charm.

```bash
juju deploy oai-ran-du-k8s --trust --channel=2.2/edge
juju deploy oai-ran-cu-k8s --trust --channel=2.2/edge
juju integrate oai-ran-du-k8s:fiveg_f1 oai-ran-cu-k8s:fiveg_f1
```

## Image

- **oai-ran-du**: `ghcr.io/canonical/oai-ran-du:2.2.0`
