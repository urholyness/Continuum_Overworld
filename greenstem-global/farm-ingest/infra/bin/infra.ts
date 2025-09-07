#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { FarmIngestStack } from '../lib/farm-stack';

const app = new cdk.App();

const env = app.node.tryGetContext('env') || 'sbx';
const stackName = `GSG-FarmIngest-${env.toUpperCase()}`;

new FarmIngestStack(app, stackName, {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
  description: `2BH Farm Dashboard Infrastructure - ${env.toUpperCase()} Environment`,
  tags: {
    Environment: env,
    Project: '2BH-Farm-Dashboard',
    ManagedBy: 'CDK',
    Owner: 'GreenStem-Global',
  },
});