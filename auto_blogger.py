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
        "title": "Kubernetes OOMKilled (Exit Code 137) Cascades Under High Load",
        "description": "How to triage, mitigate, and tune JVM cgroups when Kubernetes microservices crash with ExitCode 137 under traffic surges.",
        "tags": ["kubernetes", "devops", "sre", "cloud"],
        "scenario": "During peak hours, your primary microservice pods start restarting with ExitCode 137. Remaining pods absorb traffic and crash in cascade.",
        "triage_cmd": "kubectl describe pod <pod-name> -n prod | grep -E '(OOMKilled|Exit Code)'\nkubectl top pods -n prod --sort-by=memory\nkubectl scale deployment/api --replicas=15 -n prod",
        "root_cause": "Unset JVM MaxRAMPercentage caused container memory limits to be breached, while Horizontal Pod Autoscaler lacked memory metric rules.",
        "fix": "Configure JVM flags (-XX:MaxRAMPercentage=75.0), define memory requests/limits correctly, and enable memory-based HPA scaling.",
        "intervixa_link": "https://intervixa.online/kubernetes-scenario-questions",
        "intervixa_anchor": "Intervixa Kubernetes Scenario Question Bank"
    },
    {
        "id": 2,
        "title": "AWS NAT Gateway Cost Spikes: VPC Endpoints & Flow Logs Deep-Dive",
        "description": "Step-by-step incident response for unexpected AWS NAT Gateway data charges and S3 private routing.",
        "tags": ["aws", "devops", "cloud", "architecture"],
        "scenario": "Monthly AWS bill surges by thousands due to NAT Gateway data transfer billing between private subnets and S3.",
        "triage_cmd": "aws ec2 describe-nat-gateways --filter 'Name=state,Values=available'\naws logs start-query --log-group-name /aws/vpc/flow-logs --query-string 'stats sum(bytes) by dstAddr'\naws ec2 create-vpc-endpoint --vpc-id vpc-xxxx --service-name com.amazonaws.us-east-1.s3",
        "root_cause": "High-volume data pipelines and image pulls routing through public NAT Gateways instead of VPC Gateway Endpoints.",
        "fix": "Deploy Gateway VPC Endpoints for S3/DynamoDB and Interface Endpoints for ECR to bypass NAT Gateway data transfer fees completely.",
        "intervixa_link": "https://intervixa.online/aws-interview-questions",
        "intervixa_anchor": "Intervixa AWS Interview Questions & Scenarios"
    },
    {
        "id": 3,
        "title": "Recovering from Terraform Remote State Lock Deadlocks in S3 & DynamoDB",
        "description": "What to do when a CI/CD runner is killed midway and leaves Terraform state locked in DynamoDB.",
        "tags": ["terraform", "devops", "iac", "cicd"],
        "scenario": "A CI/CD runner times out during terraform apply, leaving DynamoDB state lock active. The entire team is blocked from deployments.",
        "triage_cmd": "terraform force-unlock <LOCK-ID>\naws dynamodb get-item --table-name terraform-locks --key '{\"LockID\": {\"S\": \"path/terraform.tfstate-md5\"}}'\nterraform plan -refresh-only",
        "root_cause": "Premature runner termination prevented Terraform from releasing the lock item in the DynamoDB table.",
        "fix": "Confirm no active background deployment is running, execute terraform force-unlock with the lock ID, and add SIGTERM traps in CI/CD runners.",
        "intervixa_link": "https://intervixa.online/terraform-interview-questions",
        "intervixa_anchor": "Intervixa Terraform Interview Questions"
    },
    {
        "id": 4,
        "title": "Docker Multi-Stage Builds & Secrets: Eliminating Leaked Credentials",
        "description": "How credentials leak into intermediate Docker layers and how BuildKit secret mounts fix it.",
        "tags": ["docker", "security", "devops", "cicd"],
        "scenario": "Security scanner detects AWS IAM keys embedded in an intermediate image layer, even though RUN rm -f .env was executed.",
        "triage_cmd": "docker history --no-trunc <image-name>\ntrufflehog docker --image <image-name>\nDOCKER_BUILDKIT=1 docker build --secret id=mysecret,src=.env .",
        "root_cause": "Docker image layers are immutable. Removing a secret in a subsequent layer does not delete it from historical layers.",
        "fix": "Use Docker BuildKit with RUN --mount=type=secret or multi-stage builds where secrets never enter final artifacts.",
        "intervixa_link": "https://intervixa.online/docker-interview-questions",
        "intervixa_anchor": "Intervixa Docker Interview Questions & Scenarios"
    },
    {
        "id": 5,
        "title": "Solving Kubernetes CrashLoopBackOff: Probe Flapping & Cold Starts",
        "description": "Deep-dive into probe flapping, connection pool starvation, and how startupProbes prevent container kill loops.",
        "tags": ["kubernetes", "sre", "devops", "troubleshooting"],
        "scenario": "A new container release enters CrashLoopBackOff because the DB connection pool takes 40s to warm up, but liveness probe kills it at 15s.",
        "triage_cmd": "kubectl describe pod <pod-name> -n prod | grep -A 5 'Liveness:'\nkubectl logs <pod-name> --previous\nkubectl get events -n prod --sort-by='.metadata.creationTimestamp'",
        "root_cause": "Aggressive liveness probe timeouts before application initialization completes, creating an infinite restart loop.",
        "fix": "Decouple readiness from liveness, and configure a dedicated startupProbe with failureThreshold=30 and periodSeconds=10.",
        "intervixa_link": "https://intervixa.online/kubernetes-scenario-questions",
        "intervixa_anchor": "Intervixa Kubernetes Scenarios"
    }
]

def build_article_markdown(t):
    lines = [
        f"In technical interviews for **Senior Cloud, DevOps, and SRE roles**, trivial syntax questions are gone. Hiring managers want to see how you respond when production is down at 2 AM.",
        "",
        f"Today, let's dissect a real-world production incident: **{t['title']}**.",
        "",
        "---",
        "",
        "## The Scenario",
        f"> **Incident Context:** {t['scenario']}",
        "",
        "When facing this situation during a live interview or outage, interviewers evaluate structured triage:",
        "1. Blast radius identification",
        "2. Immediate traffic mitigation",
        "3. Root cause isolation",
        "4. Permanent architectural hardening",
        "",
        "---",
        "",
        "## 1. Immediate Incident Triage",
        "Verify current telemetry and active states before applying code changes:",
        "",
        "```bash",
        t['triage_cmd'],
        "```",
        "",
        "---",
        "",
        "## 2. Root Cause Analysis (RCA)",
        f"**Why did this happen?**",
        "",
        t['root_cause'],
        "",
        "---",
        "",
        "## 3. Permanent Architectural Hardening",
        t['fix'],
        "",
        "---",
        "",
        "## 💡 Practice Scenarios Aloud with Live AI",
        "Knowing the fix is only half the battle. In a senior interview, how smoothly you articulate your debugging thought process under pressure determines your rating.",
        "",
        "You can practice answering these exact incident scenarios aloud with real-time audio and video feedback on the **[Intervixa Live AI Mock Interviewer](https://intervixa.online/modules/mock-interview/live)**.",
        "",
        "### Helpful Resources:",
        f"- Explore more curated questions: **[{t['intervixa_anchor']}]({t['intervixa_link']})**",
        "- Optimize your resume against ATS filters: **[Intervixa Free ATS Resume Analyzer](https://intervixa.online/modules/ats-resume-score)**",
        "- Build your personal brand: Turn your daily debugging lessons into recruiter-attracting reachouts with the **[AI LinkedIn Post Generator](https://intervixa.online/modules/linkedin-optimizer)**",
        "",
        "---",
        "*What is your team's standard operating procedure for handling this type of incident? Let's discuss in the comments below!*"
    ]
    return "\n".join(lines)

def get_next_topic_index():
    state_file = "last_posted_index.txt"
    idx = 0
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                idx = int(f.read().strip())
        except Exception:
            idx = 0
    next_idx = (idx + 1) % len(TOPICS)
    with open(state_file, "w") as f:
        f.write(str(next_idx))
    return idx

def publish_to_devto(topic):
    url = "https://dev.to/api/articles"
    body_markdown = build_article_markdown(topic)
    
    payload = {
        "article": {
            "title": f"DevOps Outage Scenario: {topic['title']}",
            "published": True,
            "body_markdown": body_markdown,
            "tags": topic["tags"],
            "series": "Real-World DevOps Scenario Drills",
            "main_image": "https://intervixa.online/og-image.png",
            "description": topic["description"]
        }
    }
    
    headers = {
        "api-key": DEVTO_API_KEY,
        "Content-Type": "application/json",
        "User-Agent": "Intervixa-AutoBlogger/1.0"
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print(f"✅ Successfully published: {res_data.get('url')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not DEVTO_API_KEY:
        print("❌ Error: DEVTO_API_KEY is missing!")
        sys.exit(1)
    idx = get_next_topic_index()
    publish_to_devto(TOPICS[idx])
