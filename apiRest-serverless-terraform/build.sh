rm -f apiRest-serverless.zip
cd lambda
zip ../apiRest-serverless.zip hello.js
cd ..

cd terraform
terraform apply
cd ..