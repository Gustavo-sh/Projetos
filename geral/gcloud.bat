@echo off

start "Porta do Postgres Reports executada" gcloud.cmd compute start-iap-tunnel vm-postgresql-robbyson-mis-1 28017 --local-host-port=127.0.0.1:29017 --project robbyson-production --zone=us-east4-c
start "Porta do RDP executada" gcloud.cmd compute start-iap-tunnel vm-mis-working-processing-1 3389 --local-host-port=127.0.0.1:3385 --project robbyson-production --zone=us-east4-c
start "Porta do Postgres AeC executada" gcloud.cmd compute start-iap-tunnel vm-postgresql-reports-2 27017 --local-host-port=127.0.0.1:26017 --project robbyson-production
