#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
import urllib.error

DEVTO_API_KEY = os.environ.get("DEVTO_API_KEY", "")

TOPICS = [
    {
        "id": 1,
        "title": "Debugging Kubernetes OOMKilled (Exit Code 137) Cascades Under Flash Traffic",
        "description": "How to diagnose, mitigate, and tune JVM/cgroups when Kubernetes pods face cascading OOMKilled crashes during high traffic.",
        "tags": ["kubernetes", "devops", "sre", "cloud"],
        "scenario": "During high concurrency, your microservice pods start restarting with ExitCode 137. The failure cascades as remaining pods absorb the load and also crash.",
        "triage_commands": [
            "kubectl describe pod <pod-name> -n production | grep -E '(OOMKilled|Exit Code)'",
            "kubectl top pods -n production --sort-by=memory",
            "kubectl scale deployment/api-gateway --replicas=15 -n production"
        ],
        "root_cause": "JVM MaxRAMPercentage unconfigured causing container memory limits to be breached, combined with missing HPA on memory metrics.",
        "fix": "Tune JVM options (-XX:MaxRAMPercentage=75.0), define proper memory requests/limits, and configure memory-based Horizontal Pod Autoscaling (HPA).",
        "intervixa_link": "https://intervixa.online/kubernetes-scenario-questions",
        "intervixa_anchor": "Intervixa Kubernetes Scenario Question Bank"
    },
    {
        "id": 2,
        "title": "AWS NAT Gateway Cost Spike: Triage, VPC Endpoints & Flow Logs Deep-Dive",
        "description": "Step-by-step incident response playbook for unexpected AWS NAT Gateway bandwidth surges and S3 private routing.",
        "tags": ["aws", "devops", "cloud", "architecture"],
        "scenario": "Your monthly AWS invoice spikes by thousands due to NAT Gateway data processing charges between private subnets and S3.",
        "triage_commands": [
            "aws ec2 describe-nat-gateways --filter 'Name=state,Values=available'",
            "aws logs start-query --log-group-name /aws/vpc/flow-logs --query-string 'stats sum(bytes) by dstAddr'",
            "aws ec2 create-vpc-endpoint --vpc-id vpc-xxxx --service-name com.amazonaws.us-east-1.s3"
        ],
        "root_cause": "High-volume data pipelines and Docker image pulls routing through public NAT Gateways instead of VPC Gateway Endpoints.",
        "fix": "Provision Gateway VPC Endpoints for S3/DynamoDB and Interface Endpoints for ECR to bypass NAT Gateway data transfer billing completely.",
        "intervixa_link": "https://intervixa.online/aws-interview-questions",
        "intervixa_anchor": "Intervixa AWS Interview Questions & Scenarios"
    },
    {
        "id": 3,
        "title": "Recovering from Terraform Remote State Lock Deadlocks in S3 & DynamoDB",
        "description": "What happens when a CI/CD deployment aborts and leaves your Terraform state locked in DynamoDB.",
        "tags": ["terraform", "devops", "iac", "cicd"],
        "scenario": "A CI/CD runner is killed midway through a terraform apply, leaving the DynamoDB state lock active. All team members are blocked with 'Error: Error acquiring the state lock'.",
        "triage_commands": [
            "terraform force-unlock <LOCK-ID>",
            "aws dynamodb get-item --table-name terraform-locks --key '{\"LockID\": {\"S\": \"path/terraform.tfstate-md5\"}}'",
            "terraform plan -refresh-only"
        ],
        "root_cause": "Premature runner termination prevented Terraform from releasing the lock item in the DynamoDB lock table.",
        "fix": "Verify no active background applies are running, safely run force-unlock with the specific Lock ID, and configure graceful SIGTERM traps in CI/CD pipelines.",
        "intervixa_link": "https://intervixa.online/terraform-interview-questions",
        "intervixa_anchor": "Intervixa Terraform Interview Questions"
    },
    {
        "id": 4,
        "title": "Docker Multi-Stage Builds & Secrets: Eliminating Leaked Credentials in Image Layers",
        "description": "How credentials leak into intermediate Docker layers and how to use BuildKit secrets to prevent supply-chain vulnerabilities.",
        "tags": ["docker", "security", "devops", "cicd"],
        "scenario": "A security scanner flags AWS IAM credentials embedded in an intermediate Docker layer, even though a subsequent RUN rm -f .env was executed.",
        "triage_commands": [
            "docker history --no-trunc <image-name>",
            "trufflehog docker --image <image-name>",
            "DOCKER_BUILDKIT=1 docker build --secret id=mysecret,src=.env ."
        ],
        "root_cause": "Docker image layers are immutable. Removing a secret in a later layer does not remove it from preceding layers.",
        "fix": "Use BuildKit's syntax=docker/dockerfile:1 with RUN --mount=type=secret or multi-stage builds where secrets never enter final artifacts.",
        "intervixa_link": "https://intervixa.online/docker-interview-questions",
        "intervixa_anchor": "Intervixa Docker Interview Questions & Scenarios"
    },
    {
        "id": 5,
        "title": "Solving Kubernetes CrashLoopBackOff: The Readiness & Liveness Probe Dilemma",
        "description": "Deep-dive into probe flapping, connection pool starvation, and how startupProbes prevent premature pod terminations.",
        "tags": ["kubernetes", "sre", "devops", "troubleshooting"],
        "scenario": "A newly deployed release enters CrashLoopBackOff because the application takes 40s to warm up DB connections, but the liveness probe kills it at 15s.",
        "triage_commands": [
            "kubectl describe pod <pod-name> -n prod | grep -A 5 'Liveness:'",
            "kubectl logs <pod-name> --previous",
            "kubectl get events -n prod --sort-by='.metadata.creationTimestamp'"
        ],
        "root_cause": "Aggressive liveness probe thresholds before application initialization is complete, causing an infinite kill-restart loop.",
        "fix": "Separate readiness from liveness, and configure a dedicated startupProbe with failureThreshold=30 and periodSeconds=10.",
        "intervixa_link": "https://intervixa.online/kubernetes-scenario-questions",
        "intervixa_anchor": "Intervixa Kubernetes Scenarios"
    }
]

def generate_article_body(topic):
    commands_formatted = "\n".join([f"$ {cmd}" for cmd in topic["triage_commands"]])
    
    return f"""In high-stakes technical interviews for **Senior Cloud, DevOps, and SRE roles**, generic syntax questions are a thing of the past. Hiring managers want to see how you respond when production is down at 2 AM.

Today, let's dissect a real-world production incident: **{topic['title']}**.

---

## The Scenario

> **Incident Context:** {topic['scenario']}

When facing this situation during a live interview or production outage, interviewers look for structured triage:
1. Identifying blast radius
2. Immediate traffic mitigation
3. Root cause isolation
4. Permanent architectural hardening

---

## 1. Immediate Incident Triage

Before jumping into code changes, verify the current telemetry and active states:

```bash
{commands_formatted}
