#
# Challenge 5. aiworkshop. Making trained model operational
#

# 1. Building Docker image
#    create empty folder (Challenge5); copy trained model, app.py, Dockerfile
 
# Building Docker image. Make sure to tun it in the filder with Dockerfile
docker build -t aimodel .

# 2. Cerating Azure Container Registry
# Login to Azure
az login
az configure # set defualt output to table and location westeurope
az account list # make sure the right subscription is user by default

az group create --name "vtsykun-ml-service"

az acr create --name vtsykuntestml --sku Basic -g "vtsykun-ml-service"
az acr login --name vtsykuntestml
az acr update --name vtsykuntestml --admin-enabled true
az acr credential show --name vtsykuntestml --query "passwords[0].value"
  -> "record this password"
az acr list --query "[].{acrLoginServer:loginServer}"
  -> "vtsykuntestml.azurecr.io" # record login server name 

# 3. Tag and push image to the new repository
docker images
docker tag aimodel vtsykuntestml.azurecr.io/aimodel:v1
docker push vtsykuntestml.azurecr.io/aimodel:v1

# 4. Check if container is in the registry and craete container
az acr repository list --name vtsykuntestml 
az container create --name vtsykuntestml -g "vtsykun-ml-service" --image vtsykuntestml.azurecr.io/aimodel:v1 --ip-address public --ports 8080 --cpu 2 --memory 8

# 5. Working with containers
az container attach --name vtsykuntestml # read logs
az container list # list of ruuning containers
az container delete --name vtsykuntestml -g "vtsykun-ml-service" # delete running container
