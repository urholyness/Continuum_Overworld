# Main Terraform configuration for Comms Agents AWS deployment

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "comms-agents-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "comms-agents"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# VPC and Networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
  
  name = "comms-agents-vpc"
  cidr = var.vpc_cidr
  
  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
  
  enable_nat_gateway = true
  single_nat_gateway = false
  one_nat_gateway_per_az = true
  
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Environment = var.environment
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "comms-agents-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = {
    Name = "comms-agents-cluster"
  }
}

# ECS Service for Switchboard
resource "aws_ecs_service" "switchboard" {
  name            = "comms-agents-switchboard"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.switchboard.arn
  desired_count   = var.switchboard_desired_count
  
  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.switchboard.arn
    container_name   = "switchboard"
    container_port   = 8000
  }
  
  depends_on = [aws_lb_listener.switchboard]
  
  tags = {
    Name = "comms-agents-switchboard"
  }
}

# ECS Task Definition for Switchboard
resource "aws_ecs_task_definition" "switchboard" {
  family                   = "comms-agents-switchboard"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.switchboard_cpu
  memory                   = var.switchboard_memory
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  
  container_definitions = jsonencode([
    {
      name  = "switchboard"
      image = "${aws_ecr_repository.switchboard.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]
      
      environment = [
        {
          name  = "APP_ENV"
          value = var.environment
        },
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.endpoint}/${var.db_name}"
        },
        {
          name  = "REDIS_URL"
          value = "redis://${aws_elasticache_cluster.redis.cache_nodes.0.address}:${aws_elasticache_cluster.redis.cache_nodes.0.port}/0"
        },
        {
          name  = "CHROMA_HOST"
          value = aws_elasticache_cluster.chromadb.cache_nodes.0.address
        },
        {
          name  = "CHROMA_PORT"
          value = tostring(aws_elasticache_cluster.chromadb.cache_nodes.0.port)
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.switchboard.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
      
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval   = 30
        timeout    = 5
        retries    = 3
        startPeriod = 60
      }
    }
  ])
  
  tags = {
    Name = "comms-agents-switchboard-task"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "comms-agents-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets
  
  enable_deletion_protection = var.environment == "production"
  
  tags = {
    Name = "comms-agents-alb"
  }
}

# ALB Target Group
resource "aws_lb_target_group" "switchboard" {
  name        = "comms-agents-switchboard-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }
  
  tags = {
    Name = "comms-agents-switchboard-tg"
  }
}

# ALB Listener
resource "aws_lb_listener" "switchboard" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.switchboard.arn
  }
}

# RDS Database
resource "aws_db_instance" "main" {
  identifier = "comms-agents-db"
  
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class
  
  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = var.db_backup_retention_period
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  multi_az               = var.environment == "production"
  publicly_accessible    = false
  skip_final_snapshot    = var.environment != "production"
  
  tags = {
    Name = "comms-agents-db"
  }
}

# RDS Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "comms-agents-db-subnet-group"
  subnet_ids = module.vpc.private_subnets
  
  tags = {
    Name = "comms-agents-db-subnet-group"
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "comms-agents-redis"
  engine               = "redis"
  node_type            = var.redis_node_type
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  security_group_ids   = [aws_security_group.redis.id]
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  
  tags = {
    Name = "comms-agents-redis"
  }
}

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "comms-agents-cache-subnet-group"
  subnet_ids = module.vpc.private_subnets
  
  tags = {
    Name = "comms-agents-cache-subnet-group"
  }
}

# ElastiCache ChromaDB
resource "aws_elasticache_cluster" "chromadb" {
  cluster_id           = "comms-agents-chromadb"
  engine               = "redis"
  node_type            = var.chromadb_node_type
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 8000
  security_group_ids   = [aws_security_group.chromadb.id]
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  
  tags = {
    Name = "comms-agents-chromadb"
  }
}

# ECR Repository
resource "aws_ecr_repository" "switchboard" {
  name                 = "comms-agents-switchboard"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  tags = {
    Name = "comms-agents-switchboard-ecr"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "switchboard" {
  name              = "/ecs/comms-agents-switchboard"
  retention_in_days = var.environment == "production" ? 30 : 7
  
  tags = {
    Name = "comms-agents-switchboard-logs"
  }
}

# Security Groups
resource "aws_security_group" "alb" {
  name        = "comms-agents-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    description = "HTTP from Internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTPS from Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "comms-agents-alb-sg"
  }
}

resource "aws_security_group" "ecs_tasks" {
  name        = "comms-agents-ecs-tasks-sg"
  description = "Security group for ECS tasks"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    description     = "HTTP from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "comms-agents-ecs-tasks-sg"
  }
}

resource "aws_security_group" "rds" {
  name        = "comms-agents-rds-sg"
  description = "Security group for RDS database"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    description     = "PostgreSQL from ECS tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "comms-agents-rds-sg"
  }
}

resource "aws_security_group" "redis" {
  name        = "comms-agents-redis-sg"
  description = "Security group for Redis"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    description     = "Redis from ECS tasks"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "comms-agents-redis-sg"
  }
}

resource "aws_security_group" "chromadb" {
  name        = "comms-agents-chromadb-sg"
  description = "Security group for ChromaDB"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    description     = "ChromaDB from ECS tasks"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "comms-agents-chromadb-sg"
  }
}

# IAM Roles
resource "aws_iam_role" "ecs_execution_role" {
  name = "comms-agents-ecs-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "comms-agents-ecs-task-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Auto Scaling
resource "aws_appautoscaling_target" "switchboard" {
  max_capacity       = var.switchboard_max_count
  min_capacity       = var.switchboard_min_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.switchboard.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "switchboard_cpu" {
  name               = "comms-agents-switchboard-cpu"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.switchboard.resource_id
  scalable_dimension = aws_appautoscaling_target.switchboard.scalable_dimension
  service_namespace  = aws_appautoscaling_target.switchboard.service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

resource "aws_appautoscaling_policy" "switchboard_memory" {
  name               = "comms-agents-switchboard-memory"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.switchboard.resource_id
  scalable_dimension = aws_appautoscaling_target.switchboard.scalable_dimension
  service_namespace  = aws_appautoscaling_target.switchboard.service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = 80.0
  }
}

# Outputs
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.switchboard.repository_url
}

output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.main.endpoint
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes.0.address
}

output "chromadb_endpoint" {
  description = "ChromaDB endpoint"
  value       = aws_elasticache_cluster.chromadb.cache_nodes.0.address
}

