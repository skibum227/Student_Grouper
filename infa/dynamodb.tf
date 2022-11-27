# For reference
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table

# Create the dynamo db table
resource "aws_dynamodb_table" "roster_storage" {
 name = "class_roster_storage"
 billing_mode = "PROVISIONED"
 read_capacity= "25"
 write_capacity= "25"
 attribute {
  name = "class_name"
  type = "S"
 }
 hash_key = "class_name"
}
