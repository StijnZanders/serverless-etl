from mergedeep import merge

def combine_configurations(configurations: []):
    terraform_configuration = merge({}, *configurations)

    return terraform_configuration