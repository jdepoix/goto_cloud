with open('context_dump.txt', 'w+') as file:
    # during execution CONTEXT will contain information about the migration, which should help writing more useful
    # scripts
    file.write(str(CONTEXT))
