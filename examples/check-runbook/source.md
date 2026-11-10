# Payment Service Deployment Runbook

## Overview

This runbook describes how the payment service should be deployed to production. The service has been running on the new cluster since March; it consists of three components, i.e. the API gateway, the worker pool and the ledger database, which are deployed independently and which must be upgraded in a specific order in order to avoid data inconsistencies between the ledger and the workers.

Deployments may only be carried out by on-call engineers. If you aren't on the on-call rota, don't proceed.

## Procedure

1. Prior to commencing the deployment, verify that all CI checks have passed and ensure the release tag is correct.
2. The maintenance banner should be enabled by the operator via the admin console.
3. Run `./scripts/drain.sh payments` and wait until the queue depth has dropped below 100, then scale the worker pool down to zero and take a database snapshot.
4. Deploy the ledger migration utilizing the `migrate` job.
5. Check the migration logs for errors.
6. Once the migration is finished, the API gateway and workers can be deployed.
7. Turn off the maintenance banner.

WARNING: Extreme care should be exercised when running the rollback script, as it will drop the new ledger tables.

Note: Make sure you notify the #payments channel after the deployment.

## Rollback

Rollback is usually straightforward. It's performed by re-deploying the previous release tag, etc. The payment service production cluster ledger database migration rollback job has to be triggered manually.
