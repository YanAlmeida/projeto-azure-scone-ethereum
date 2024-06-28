variable "prefix" {
  description = "A prefix used for naming resources."
}

variable "location" {
  description = "Azure region for deployment."
}

variable "resource_group_name" {
  description = "Resource group name"
  default     = "pgc-resources"
}

variable "public_key_ssh" {
  description = "Public key for SSH access"
}

variable "dockerhub_image_sgx" {
  description = "Docker image for SGX instance."
  default = "yanalmeida91/sgx-blockchain-pull:latest"
}

variable "dockerhub_image_sgx_untrusted" {
  description = "Docker image for untrusted SGX instance run."
  default = "yanalmeida91/sgx-untrusted-blockchain-pull:ganache"
}

variable "dockerhub_image_nginx" {
  description = "Docker image for nginx repository."
  default = "yanalmeida91/nginx-file-repo:latest"
}

variable "sgx_driver_distro_name" {
  description = "Distro name for URL to download SGX driver"
  default     = "ubuntu20.04-server"
}

variable "sgx_driver_file_name" {
  description = "Filename for URL to download SGX driver"
  default     = "sgx_linux_x64_driver_2.11.54c9c4c.bin"
}

variable "contract_abi" {
  description = "ABI do contrato inteligente"
  default     = "[{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"_machine\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"_value\",\"type\":\"uint256\"}],\"name\":\"ReturnUInt\",\"type\":\"event\"},{\"inputs\":[],\"name\":\"collectResults\",\"outputs\":[{\"internalType\":\"bool\",\"name\":\"\",\"type\":\"bool\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"connectMachine\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"connectedMachines\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"disconnectMachine\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"disconnectedMachines\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256[]\",\"name\":\"idList\",\"type\":\"uint256[]\"}],\"name\":\"getJobs\",\"outputs\":[{\"internalType\":\"uint256[]\",\"name\":\"jobIds\",\"type\":\"uint256[]\"},{\"internalType\":\"string[]\",\"name\":\"fileUrls\",\"type\":\"string[]\"},{\"internalType\":\"uint256[]\",\"name\":\"startingTimes\",\"type\":\"uint256[]\"},{\"internalType\":\"uint256[]\",\"name\":\"processingTimes\",\"type\":\"uint256[]\"},{\"internalType\":\"uint256[]\",\"name\":\"endingTimes\",\"type\":\"uint256[]\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256[]\",\"name\":\"_jobsIds\",\"type\":\"uint256[]\"}],\"name\":\"getJobsMachine\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"limite\",\"type\":\"uint256\"}],\"name\":\"getJobsMachineView\",\"outputs\":[{\"internalType\":\"uint256[]\",\"name\":\"jobsIds\",\"type\":\"uint256[]\"},{\"internalType\":\"string[]\",\"name\":\"fileUrls\",\"type\":\"string[]\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"_jobId\",\"type\":\"uint256\"}],\"name\":\"getResult\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"charCount\",\"type\":\"uint256\"},{\"internalType\":\"string\",\"name\":\"message\",\"type\":\"string\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"heartBeat\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"jobProcessingInfo\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"waitingTimestamp\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"processingTimestamp\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"currentStatus\",\"type\":\"uint256\"},{\"internalType\":\"address\",\"name\":\"responsibleMachine\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"indexInJobs\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"indexInMachine\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"processedTimestamp\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"jobProcessingMaxTime\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"jobUpdateInterval\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"jobs\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"jobsPerAddress\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"jobsPerId\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"jobId\",\"type\":\"uint256\"},{\"internalType\":\"string\",\"name\":\"fileUrl\",\"type\":\"string\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"lastJobId\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"processedJobs\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"resetProcessedJobs\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"resultsPerJobId\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"jobId\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"charCount\",\"type\":\"uint256\"},{\"internalType\":\"string\",\"name\":\"message\",\"type\":\"string\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"returnJobsIds\",\"outputs\":[{\"internalType\":\"uint256[]\",\"name\":\"jobIds\",\"type\":\"uint256[]\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"bool\",\"name\":\"value\",\"type\":\"bool\"}],\"name\":\"setResultValue\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"string\",\"name\":\"url\",\"type\":\"string\"}],\"name\":\"submitJob\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"_jobId\",\"type\":\"uint256\"}],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"string[]\",\"name\":\"urls\",\"type\":\"string[]\"}],\"name\":\"submitJobBatch\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256[]\",\"name\":\"_jobsIds\",\"type\":\"uint256[]\"},{\"internalType\":\"uint256[]\",\"name\":\"_charCounts\",\"type\":\"uint256[]\"},{\"internalType\":\"string[]\",\"name\":\"_messages\",\"type\":\"string[]\"}],\"name\":\"submitResults\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"}]"
}

variable "contract_address" {
  description = "Endereço do contrato inteligente"
  default     = "0x5b92A0289CBeBacC143842122bC3c5B78e5584FB"
}

variable "number_machines" {
    description = "Numero de maquinas a criar"
    default     = 1
}

variable "enclave_key_path" {
  description = "Caminho para o arquivo contendo o enclave-key.pem"
}

variable "manifest_path" {
  description = "Caminho para o arquivo contendo o manifesto"
}

variable "generate_public_ip" {
  description = "Se deve ou não gerar ip publico para as máquinas"
  type        = list(bool)
}

variable "number_untrusted_containers" {
  description = "Se deve ou não gerar ip publico para as máquinas"
  type        = number
}


variable "aws_region" {
  description = "AWS region for deployment."
  default     = "us-east-2"
}

variable "aws_availability_zone" {
  description = "AWS availability zone for subnet."
  default     = "us-east-2a"
}

variable "dockerhub_image_blockchain" {
  description = "Docker image for blockchain instance."
  default = "yanalmeida91/ganache-smart-contract:latest"
}

variable "aws_access_key" {
  description = "AWS Access Key"
  type        = string
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS Secret Key"
  type        = string
  sensitive   = true
}

variable "azure_client_id" {
  description = "Azure Client ID"
  type        = string
  sensitive   = true
}

variable "azure_client_secret" {
  description = "Azure Client Secret"
  type        = string
  sensitive   = true
}

variable "azure_tenant_id" {
  description = "Azure Tenant ID"
  type        = string
  sensitive   = true
}

variable "azure_subscription_id" {
  description = "Azure Subscription ID"
  type        = string
  sensitive   = true
}