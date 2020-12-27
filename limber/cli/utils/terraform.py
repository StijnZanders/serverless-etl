def combine_configurations(configurations: []):
    terraform_configuration = {}

    # List of configurations
    for configuration in configurations:

        # Dict of configuration types (data or resource)
        for configuration_type in configuration:

            # If the configuration type is not yet in the config then add
            if configuration_type not in terraform_configuration:
                terraform_configuration[configuration_type] = {}

            # List object types (pub_sub_topic, cloud_function)
            for object_type in configuration[configuration_type]:

                # If object type not yet there then add
                if object_type not in terraform_configuration[configuration_type]:
                    terraform_configuration[configuration_type][object_type] = {}

                # List over objects of that type
                for o in configuration[configuration_type][object_type]:

                    # List over keys of object (just 1 key anyway)
                    for key in o:
                        terraform_configuration[configuration_type][object_type][key] = o[key]

    return terraform_configuration