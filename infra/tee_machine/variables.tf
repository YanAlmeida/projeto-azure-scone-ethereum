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

variable "ssh_access_ip_address" {
  description = "IP acesso SSH."
}

variable "public_key_ssh" {
  description = "Public key for SSH access"
}

variable "dockerhub_image_sgx" {
  description = "Docker image for SGX instance."
}

variable "dockerhub_image_sgx_untrusted" {
  description = "Docker image for untrusted SGX instance run."
}

variable "dockerhub_image_nginx" {
  description = "Docker image for nginx repository."
}

variable "sgx_driver_distro_name" {
  description = "Distro name for URL to download SGX driver"
  default     = "ubuntu20.04-server"
}

variable "sgx_driver_file_name" {
  description = "Filename for URL to download SGX driver"
  default     = "sgx_linux_x64_driver_2.11.54c9c4c.bin"
}

variable "subnet_id" {
  description = "Subnet ID"
}

variable "public_ip_blockchain" {
  description = "Public IP of the blockchain machine"
}

variable "contract_abi" {
  description = "ABI do contrato inteligente"
  default     = "[{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"internalType\":\"address\",\"name\":\"_machine\",\"type\":\"address\"},{\"indexed\":false,\"internalType\":\"uint256\",\"name\":\"_value\",\"type\":\"uint256\"}],\"name\":\"ReturnUInt\",\"type\":\"event\"},{\"inputs\":[],\"name\":\"connectMachine\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"connectedMachines\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"disconnectMachine\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"disconnectedMachines\",\"outputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"getJobs\",\"outputs\":[{\"internalType\":\"uint256[]\",\"name\":\"jobIds\",\"type\":\"uint256[]\"},{\"internalType\":\"string[]\",\"name\":\"fileUrls\",\"type\":\"string[]\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256[]\",\"name\":\"_jobsIds\",\"type\":\"uint256[]\"}],\"name\":\"getJobsMachine\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"getJobsMachineView\",\"outputs\":[{\"internalType\":\"uint256[]\",\"name\":\"jobsIds\",\"type\":\"uint256[]\"},{\"internalType\":\"string[]\",\"name\":\"fileUrls\",\"type\":\"string[]\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"_jobId\",\"type\":\"uint256\"}],\"name\":\"getResult\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"charCount\",\"type\":\"uint256\"},{\"internalType\":\"string\",\"name\":\"message\",\"type\":\"string\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"heartBeat\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"jobProcessingInfo\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"waitingTimestamp\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"processingTimestamp\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"currentStatus\",\"type\":\"uint256\"},{\"internalType\":\"address\",\"name\":\"responsibleMachine\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"indexInJobs\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"indexInMachine\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"processedTimestamp\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"jobProcessingMaxTime\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"jobUpdateInterval\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"jobWaitingMaxTime\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"jobs\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"address\",\"name\":\"\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"jobsPerAddress\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"jobsPerId\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"jobId\",\"type\":\"uint256\"},{\"internalType\":\"string\",\"name\":\"fileUrl\",\"type\":\"string\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"\",\"type\":\"uint256\"}],\"name\":\"resultsPerJobId\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"jobId\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"charCount\",\"type\":\"uint256\"},{\"internalType\":\"string\",\"name\":\"message\",\"type\":\"string\"}],\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"string\",\"name\":\"url\",\"type\":\"string\"}],\"name\":\"submitJob\",\"outputs\":[{\"internalType\":\"uint256\",\"name\":\"_jobId\",\"type\":\"uint256\"}],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[{\"internalType\":\"uint256[]\",\"name\":\"_jobsIds\",\"type\":\"uint256[]\"},{\"internalType\":\"uint256[]\",\"name\":\"_charCounts\",\"type\":\"uint256[]\"},{\"internalType\":\"string[]\",\"name\":\"_messages\",\"type\":\"string[]\"}],\"name\":\"submitResults\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"}]"
}

variable "contract_address" {
  description = "Endereço do contrato inteligente"
  default     = "0x5b92A0289CBeBacC143842122bC3c5B78e5584FB"
}

variable "account_index" {
  description = "Index da conta utilizada pela máquina SGX"
  default     = 0
}

variable "enclave_key_path" {
  description = "Caminho para o arquivo contendo o enclave-key.pem"
}

variable "manifest_path" {
  description = "Caminho para o arquivo contendo o manifesto"
}

variable "generate_public_ip" {
  description = "Se deve ou não gerar ip publico para as máquinas"
  type        = bool
}

variable "number_untrusted_containers" {
  description = "Numero de containers nao confiaveis a gerar"
  type        = number
}