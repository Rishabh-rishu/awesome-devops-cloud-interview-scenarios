# 🚀 Awesome Cloud & DevOps Scenario-Based Interview Questions (2026 Edition)

A curated collection of real-world production outage, high-availability architecture, and incident-response interview scenarios for **Cloud Engineers, DevOps Engineers, and Site Reliability Engineers (SREs)**.

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Interactive Practice](https://img.shields.io/badge/Live_Practice-Intervixa_AI-blue)](https://intervixa.online/)

---

## 🎯 Why This Repository?

Most interview cheat sheets test simple trivia (e.g., *"What is a Kubernetes Pod?"*). In modern technical interviews (especially at senior and staff levels), interviewers test **real production scenarios**:
- *"Your cluster is running at 98% memory and pods are getting OOMKilled in a cascade. How do you triage under 5 minutes?"*
- *"A developer pushed a bad Terraform commit that corrupted remote state. What is your recovery protocol?"*

This repository aggregates these high-frequency scenarios with structured answers, root-cause analyses, and mitigation steps.

> 💡 **Interactive AI Mock Practice:**
> If you want to practice answering these scenario questions aloud under timed pressure with instant feedback, practice on the [Intervixa Live AI Interviewer](https://intervixa.online/modules/mock-interview/live).

---

## 📚 Table of Contents

1. [Kubernetes Production Scenarios](#1-kubernetes-production-scenarios)
2. [AWS Cloud Architecture & Outage Scenarios](#2-aws-cloud-architecture--outage-scenarios)
3. [Docker & Container Debugging](#3-docker--container-debugging)
4. [CI/CD & GitOps Pipeline Failures](#4-cicd--gitops-pipeline-failures)
5. [Terraform & Infrastructure as Code (IaC) Scenarios](#5-terraform--infrastructure-as-code-iac-scenarios)
6. [Resume & ATS Optimization](#6-resume--ats-optimization)

---

## 1. Kubernetes Production Scenarios

### Scenario 1.1: The Cascading `OOMKilled` Loop
**Problem:** During a peak traffic event, Pods running a Java microservice start restarting with `ExitCode 137 (OOMKilled)`. As pods die, remaining pods take increased load and also crash.
- **Root Cause:** Container memory limit is set below JVM heap allocation threshold, combined with missing horizontal pod autoscaling (HPA) metrics on memory utilization.
- **Triage Steps:**
  1. Inspect pod events: `kubectl describe pod <pod-name> -n production`
  2. Check current limits vs requests: `kubectl get pod <pod-name> -o jsonpath='{.spec.containers[*].resources}'`
  3. Immediate mitigation: Scale deployment replicas manually (`kubectl scale --replicas=10 deployment/<name>`) to distribute incoming load.
  4. Permanent fix: Tune JVM ergonomics (`-XX:MaxRAMPercentage=75.0`), set appropriate container resource limits, and configure HPA.
- **Full Question Set:** [Explore 50+ Kubernetes Scenario Questions on Intervixa](https://intervixa.online/kubernetes-scenario-questions)

### Scenario 1.2: `CrashLoopBackOff` Due to Readiness Probe Misconfiguration
**Problem:** New deployment rollout starts, but none of the new pods receive traffic, and old pods are terminated prematurely.
- **Root Cause:** `initialDelaySeconds` on readiness probe is too short. The application takes 45 seconds to establish DB connection pools, but the probe fires at 10 seconds, failing 3 times and marking the pod unready.
- **Solution:** Configure `initialDelaySeconds: 45` or utilize startup probes (`startupProbe`) with failure threshold to allow slow initialization without killing the pod.

---

## 2. AWS Cloud Architecture & Outage Scenarios

### Scenario 2.1: Cross-AZ Latency & High NAT Gateway Data Transfer Costs
**Problem:** AWS monthly invoice shows an unexpected 400% surge in VPC NAT Gateway processing charges, and API p99 latency increased by 65ms.
- **Root Cause:** High-volume S3 data ingestion traffic is routing through the public NAT Gateway instead of an internal S3 Gateway VPC Endpoint.
- **Mitigation:**
  1. Provision an **S3 Gateway Endpoint** in the VPC (free of charge for transfer).
  2. Update VPC route tables to route `s3.amazonaws.com` traffic through the prefix list `pl-xxxx`.
- **Full AWS Prep:** [AWS DevOps Interview Questions on Intervixa](https://intervixa.online/aws-interview-questions)

---

## 3. Docker & Container Debugging

### Scenario 3.1: Docker Build Hangs on Insecure Private Registry in CI
**Problem:** CI pipeline suddenly hangs during `docker build` and fails after a 30-minute timeout when pushing images.
- **Root Cause:** BuildKit daemon cannot resolve internal DNS or MTU packet size mismatch on Docker network bridge.
- **Solution:** Specify `--network=host` or configure `/etc/docker/daemon.json` with appropriate MTU and DNS resolvers.
- **Full Docker Prep:** [Docker Interview Questions on Intervixa](https://intervixa.online/docker-interview-questions)

---

## 4. CI/CD & GitOps Pipeline Failures

### Scenario 4.1: Secret Leak in Docker Layer History
**Problem:** An engineer accidentally baked an AWS secret key into a Docker layer during `docker build`, pushed to a staging registry, then removed it in the next commit.
- **Mitigation:**
  1. Immediately rotate the AWS IAM credential in AWS Console / Secrets Manager.
  2. Use multi-stage Docker builds or `--mount=type=secret` so credentials never persist in intermediate image layers.
  3. Scan repository with tools like `trufflehog` and `gitleaks`.

---

## 5. Terraform & Infrastructure as Code (IaC) Scenarios

### Scenario 5.1: Remote State Lock Deadlock in S3/DynamoDB
**Problem:** CI pipeline crashed midway during `terraform apply`, leaving the state locked in DynamoDB. All subsequent deployments fail with `Error: Error acquiring the state lock`.
- **Mitigation:**
  1. Verify no ongoing apply job is running.
  2. Extract Lock ID from error message.
  3. Run: `terraform force-unlock <LOCK-ID>`
- **Full IaC Guide:** [Terraform Interview Questions on Intervixa](https://intervixa.online/terraform-interview-questions)

---

## 6. Resume & ATS Optimization

When applying for Cloud & DevOps roles, over 70% of resumes are filtered out by Applicant Tracking Systems (ATS) due to formatting errors or missing skills syntax.

- Avoid 2-column graphics-heavy templates.
- Explicitly list technologies in context: e.g., *"Automated Kubernetes cluster provisioning using Terraform, reducing deployment time by 40%"*.
- **Free ATS Audit:** Check your resume score against real job descriptions using the [Intervixa ATS Resume Analyzer](https://intervixa.online/modules/ats-resume-score) and read the [ATS Optimization Guide](https://intervixa.online/guide/ats-optimization).

---

## 🤝 Contributing

Contributions are welcome! If you have faced a tricky scenario in a real production incident or interview:
1. Fork this repository.
2. Add your scenario under the respective section.
3. Submit a Pull Request.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
