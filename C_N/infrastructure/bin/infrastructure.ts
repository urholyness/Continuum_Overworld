#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { CNFoundationStack } from '../lib/c_n-foundation-stack';

const app = new cdk.App();
new CNFoundationStack(app, 'CNFoundationStack', {
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION 
  },
  description: 'C_N Foundation Infrastructure - Core services and cost controls'
});