#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

def validate_free_tier(template_path):
    """Validate CloudFormation template against free tier rules."""
    
    with open(template_path) as f:
        template = json.load(f)
    
    resources = template.get("Resources", {})
    violations = []
    
    # Gate 1: No NAT Gateways
    for name, resource in resources.items():
        if resource.get("Type") == "AWS::EC2::NatGateway":
            violations.append(f"❌ Gate 1 FAILED: NAT Gateway found ({name})")
    
    # Gate 2: No VPC Endpoints
    for name, resource in resources.items():
        if resource.get("Type") == "AWS::EC2::VPCEndpoint":
            violations.append(f"❌ Gate 2 FAILED: VPC Endpoint found ({name})")
    
    # Gate 3: RDS must be db.t3.micro or db.t4g.micro
    for name, resource in resources.items():
        if resource.get("Type") == "AWS::RDS::DBInstance":
            instance_class = resource.get("Properties", {}).get("DBInstanceClass", "")
            if instance_class not in ["db.t3.micro", "db.t4g.micro"]:
                violations.append(f"❌ Gate 3 FAILED: RDS instance {name} is {instance_class}, must be db.t3.micro or db.t4g.micro")
    
    # Gate 4: RDS storage must be ≤ 20GB
    for name, resource in resources.items():
        if resource.get("Type") == "AWS::RDS::DBInstance":
            storage = resource.get("Properties", {}).get("AllocatedStorage", 0)
            if int(storage) > 20:
                violations.append(f"❌ Gate 4 FAILED: RDS {name} has {storage}GB storage, max is 20GB")
    
    # Gate 5: RDS must be single-AZ
    for name, resource in resources.items():
        if resource.get("Type") == "AWS::RDS::DBInstance":
            multi_az = resource.get("Properties", {}).get("MultiAZ", False)
            if multi_az:
                violations.append(f"❌ Gate 5 FAILED: RDS {name} has MultiAZ enabled")
    
    # Gate 6: Lambda memory must be ≤ 512MB
    for name, resource in resources.items():
        if resource.get("Type") == "AWS::Lambda::Function":
            memory = resource.get("Properties", {}).get("MemorySize", 128)
            if int(memory) > 512:
                violations.append(f"❌ Gate 6 FAILED: Lambda {name} has {memory}MB memory, max is 512MB")
    
    # Gate 7: No Lambda Provisioned Concurrency
    for name, resource in resources.items():
        if resource.get("Type") == "AWS::Lambda::Alias":
            if "ProvisionedConcurrencyConfig" in resource.get("Properties", {}):
                violations.append(f"❌ Gate 7 FAILED: Lambda {name} has Provisioned Concurrency")
    
    # Gate 8: No ECR repositories
    for name, resource in resources.items():
        if resource.get("Type") == "AWS::ECR::Repository":
            violations.append(f"❌ Gate 8 FAILED: ECR Repository found ({name})")
    
    # Gate 9: No ECS/Fargate
    for name, resource in resources.items():
        if resource.get("Type") in ["AWS::ECS::Cluster", "AWS::ECS::Service", "AWS::ECS::TaskDefinition"]:
            violations.append(f"❌ Gate 9 FAILED: ECS/Fargate resource found ({name})")
    
    # Gate 10: API Gateway must be REST API (not HTTP API with custom domain)
    for name, resource in resources.items():
        if resource.get("Type") == "AWS::ApiGatewayV2::Api":
            violations.append(f"❌ Gate 10 FAILED: HTTP API found ({name}), use REST API instead")
    
    return violations

def main():
    cdk_out = Path("cdk.out")
    
    if not cdk_out.exists():
        print("❌ cdk.out directory not found. Run 'cdk synth' first.")
        sys.exit(1)
    
    all_violations = []
    
    # Check all CloudFormation templates
    for template_file in cdk_out.glob("*.template.json"):
        print(f"\n��� Validating {template_file.name}...")
        violations = validate_free_tier(template_file)
        
        if violations:
            all_violations.extend(violations)
            for v in violations:
                print(f"  {v}")
        else:
            print(f"  ✅ All gates passed")
    
    if all_violations:
        print(f"\n❌ FREE TIER VALIDATION FAILED")
        print(f"Found {len(all_violations)} violation(s)")
        sys.exit(1)
    else:
        print(f"\n✅ FREE TIER VALIDATION PASSED")
        print("All 10 security gates passed. Safe to deploy.")
        sys.exit(0)

if __name__ == "__main__":
    main()
