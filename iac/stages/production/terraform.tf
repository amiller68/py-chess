terraform {
  cloud {
    organization = "krondor-chess-org"

    workspaces {
      name = "krondor-chess-production"
    }
  }
}
