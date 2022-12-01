# dapr-binding-k8s-demo
=======
# Hello Kubernetes

This tutorial will get you up and running with Dapr in a Kubernetes cluster. You will be deploying the same applications from [Hello World](../hello-world). To recap, the Python App generates messages and the Node app consumes and persists them. The following architecture diagram illustrates the components that make up this quickstart:

![Architecture Diagram](./img/Architecture_Diagram.png)

## Prerequisites

This quickstart requires you to have the following installed on your machine:

- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- A Kubernetes cluster, such as [Minikube](https://docs.dapr.io/operations/hosting/kubernetes/cluster/setup-minikube/), [AKS](https://docs.dapr.io/operations/hosting/kubernetes/cluster/setup-aks/) or [GKE](https://cloud.google.com/kubernetes-engine/)
- Azure ServiceBus in place

Also, unless you have already done so, clone the repository with the quickstarts and `cd` into the right directory:

```
git clone [-b <dapr_version_tag>]
```

## Step 1 - Setup Dapr on your Kubernetes cluster

The first thing you need is an RBAC enabled Kubernetes cluster. This could be running on your machine using Minikube, or it could be a fully-fledged cluster in Azure using [AKS](https://azure.microsoft.com/en-us/services/kubernetes-service/).

Once you have a cluster, follow the steps below to deploy Dapr to it. For more details, see [Deploy Dapr on a Kubernetes cluster](https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-deploy/).

> Please note, the CLI will install to the dapr-system namespace by default. If this namespace does not exist, the CLI will create it.
> If you need to deploy to a different namespace, you can use `-n mynamespace`.

```
dapr init --kubernetes --wait
```

Sample output:

```
⌛  Making the jump to hyperspace...
  Note: To install Dapr using Helm, see here: https://docs.dapr.io/getting-started/install-dapr-kubernetes/#install-with-helm-advanced

✅  Deploying the Dapr control plane to your cluster...
✅  Success! Dapr has been installed to namespace dapr-system. To verify, run `dapr status -k' in your terminal. To get started, go here: https://aka.ms/dapr-getting-started
```

> Without the `--wait` flag the Dapr CLI will exit as soon as the kubernetes deployments are created. Kubernetes deployments are asyncronous by default, so we use `--wait` here to make sure the dapr control plane is completely deployed and running before continuing.

<!-- STEP
name: Check dapr status
-->

```bash
dapr status -k
```

<!-- END_STEP -->

You will see output like the following. All services should show `True` in the HEALTHY column and `Running` in the STATUS column before you continue.

```
  NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
  dapr-operator          dapr-system  True     Running  1         1.0.1    13s  2021-03-08 11:00.21
  dapr-placement-server  dapr-system  True     Running  1         1.0.1    13s  2021-03-08 11:00.21
  dapr-dashboard         dapr-system  True     Running  1         0.6.0    13s  2021-03-08 11:00.21
  dapr-sentry            dapr-system  True     Running  1         1.0.1    13s  2021-03-08 11:00.21
  dapr-sidecar-injector  dapr-system  True     Running  1         1.0.1    13s  2021-03-08 11:00.21
```

## Step 2 - Create and configure Azure ServiceBus Component

Dapr can use a number of different state stores (ServiceBus, Redis, CosmosDB, DynamoDB, Cassandra, etc) to persist and retrieve state. This demo will use Redis.

1. Follow [these steps] TO DEFINE to create Azure ServiceBus message queue.
2. Once your store is created, add the keys to the `servicebus.yaml` file in the `deploy` directory.
3. Apply the `servicebus.yaml` file and observe that your state store was successfully configured!

<!-- STEP
name: Deploy redis config
sleep: 1
expected_stdout_lines:
  - "component.dapr.io/servicebus created"
-->

```bash
kubectl apply -f ./deploy/servicebus.yaml
```

<!-- END_STEP -->

```bash
component.dapr.io/servicebus created
```

## Step 3 - Deploy the Python app with the Dapr sidecar

<!-- STEP
name: Deploy Python App
sleep: 70
expected_stdout_lines:
  - "deployment.apps/pythonapp created"
  - 'deployment "pythonapp" successfully rolled out'
-->

```bash
kubectl apply -f ./deploy/python.yaml
```

Kubernetes deployments are asyncronous. This means you'll need to wait for the deployment to complete before moving on to the next steps. You can do so with the following command:

```bash
kubectl rollout status deploy/pythonapp
```

<!-- END_STEP -->

This will deploy the Python app to Kubernetes. The Dapr control plane will automatically inject the Dapr sidecar to the Pod. If you take a look at the `python.yaml` file, you will see how Dapr is enabled for that deployment:

`dapr.io/enabled: true` - this tells the Dapr control plane to inject a sidecar to this deployment.

`dapr.io/app-id: pythonapp` - this assigns a unique id or name to the Dapr application, so it can be sent messages to and communicated with by other Dapr apps.
`dapr.io/app-port: 3000` - this tells the Dapr control plane that our app is running in port 3000, and will fetch events from this port.

`dapr.io/enable-api-logging: "true"` - this is added to python.yaml file by default to see the API logs.

You'll also see the container image that you're deploying. If you want to update the code and deploy a new image, see **Next Steps** section.

<!-- END_STEP -->


## Step 4 - Verify Service

> **Optional**: Now it would be a good time to get acquainted with the [Dapr dashboard](https://docs.dapr.io/reference/cli/dapr-dashboard/). Which is a convenient interface to check status, information and logs of applications running on Dapr. The following command will make it available on http://localhost:9999/.

```bash
dapr dashboard -k -p 9999
```

## Step 5 - Review the Python app

Next, take a quick look at the Python app. Navigate to the Python app in the kubernetes quickstart: `cd python` and open `app.py`.

At a quick glance, this is a basic Python app that listens to POST messages on the '/servicebus' path on `localhost:3000`. 
Dapr knows that our python app is running on port 3000, and will send messages using POST method to this path.

`@app.route("/servicebus", methods=['POST'])`

Notice that 'servicebus' is the name of Dapr component we created in deploy/servicebus.yaml. 

The block of code comes right after tells our app
how to handle the messages coming from the ServiceBus. 
NOTE: messages from Azure ServiceBus should be sent as application/json type.


## Step 6 - Create Azure ServiceBus messages

Login to Azure Portal>Azure Service Bus>Queues>Queue Name>Service Bus Explorer>Send Message>CTRL-C+CTRL-V the sample.json content>Content Type set to 'application/json'>Send.

## Step 7 - Observe API call logs

Now that the Node.js and Python applications are deployed, watch API call logs come through:

Get the API call logs of the python app:

<!-- STEP -->

```bash
kubectl logs --selector=app=python -c daprd --tail=-1
```

<!-- END_STEP -->

When save state API calls are made, you should see logs similar to this:

```
time="2022-04-25T22:46:09.82121774Z" level=info msg="HTTP API Called: POST /v1.0/state/statestore" app_id=nodeapp instance=nodeapp-7dd6648dd4-7hpmh scope=dapr.runtime.http-info type=log ver=1.7.2
time="2022-04-25T22:46:10.828764787Z" level=info msg="HTTP API Called: POST /v1.0/state/statestore" app_id=nodeapp instance=nodeapp-7dd6648dd4-7hpmh scope=dapr.runtime.http-info type=log ver=1.7.2
```

Get the API call logs of the Python app:

<!-- STEP -->

```bash
kubectl logs pythonapp-576d79f5d6-c5bgx -c python --tail=-1
```
<!-- END_STEP -->

```
Received json message from ServiceBus!
{'data': {'orderId': '42'}}
127.0.0.1 - - [01/Dec/2022 15:19:45] "POST /servicebus HTTP/1.1" 200 -
```

## Step 7 - Cleanup

Once you're done, you can spin down your Kubernetes resources by navigating to the `./deploy` directory and running:

<!-- STEP
name: "Deploy Kubernetes"
working_dir: "./deploy"
sleep: 10
expected_stdout_lines:
  - deployment.apps "pythonapp" deleted
  - component.dapr.io "statestore" deleted
-->

```bash
kubectl delete -f .
```

<!-- END_STEP -->

This will spin down each resource defined by the .yaml files in the `deploy` directory, including the state component.

## Deploying your code

Now that you're successfully working with Dapr, you probably want to update the code to fit your scenario. The Node.js and Python apps that make up this quickstart are deployed from container images hosted on a private [Azure Container Registry](https://azure.microsoft.com/en-us/services/container-registry/). To create new images with updated code, you'll first need to install docker on your machine. Next, follow these steps:

1. Update Python code as you see fit!
2. Navigate to the directory of the app you want to build a new image for.
3. Run `docker build -t <YOUR_IMAGE_NAME> . `. You can name your image whatever you like. If you're planning on hosting it on docker hub, then it should start with `<YOUR_DOCKERHUB_USERNAME>/`.
4. Once your image has built you can see it on your machines by running `docker images`.
5. To publish your docker image to docker hub (or another registry), first login: `docker login`. Then run`docker push <YOUR IMAGE NAME>`.
6. Update your .yaml file to reflect the new image name.
7. Deploy your updated Dapr enabled app: `kubectl apply -f <YOUR APP NAME>.yaml`.
