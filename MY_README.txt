*********************************************************************************
How to fix INPUT BUG in Workstation 17.5
(NOT WORKING)
In admin PowerShell run following command:
Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux

EXAMPLE
PS C:\windows\system32> Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux                                                                                                                                                                                                                                                                                                          PS C:\windows\system32> Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
Path          :
Online        : True
RestartNeeded : False

Potentionally works:
in vmx configuration set following options:
keyboard.allowBothIRQs = "FALSE"
keyboard.vusb.enable = "TRUE"



********************************************************************************
How to run Jenkins user as robo user on UBUNTU (e.g. when robo user is the only user with configured DB2 installation)
STEPS:
1. Open the sudoers file: Use visudo to edit the sudoers file, which is typically located at /etc/sudoers.
sudo visudo
2. Add a sudo entry for the Jenkins user: So the section that in sudoers will look like this:
   # User privilege specification
   root    ALL=(ALL:ALL) ALL
   jenkins ALL=(robo) NOPASSWD:ALL
3. Restart Jenkins : To make changes in the sudoers file active, restart the Jenkins service:
      sudo systemctl restart jenkins
4. Now, in Jenkins processes you can run db2start using following syntax:  sudo -u robo -i db2start


Example of Jenkins execution as robo user:
stage('buildStepCompilingAndLinking') {
            steps {
                sh "cd /QA/EZTRV116QA/EZTRV116/GA/BUILD"
                sh "sudo -u robo -i db2start"
                sh "sudo -u robo -i  db2 connect to SAMPLE "
                sh "/QA/LinuxEztBuildScripting/BuildDebugFull.sh"
            }
        }
Full Jenkins pipeline:
pipeline {
    agent any

    stages {
        stage('Preparation') {
            steps {
                echo 'Preparing for full rebuild of Debug version of Easytrieve on Linux...'
            }
        }
        stage('buildStepCompilingAndLinking') {
            steps {
                // Ensure the working directory exists and is accessible
                sh "cd /QA/EZTRV116QA/EZTRV116/GA/BUILD"

                // Activate DB2 and ignore any errors
                script {
                    try {
                        sh "sudo -u robo -i db2start"
                        println("DB2 start executed successfully")
                    } catch (Exception e) {
                        println("Error occurred while starting DB2: ${e.getMessage()}")
                        // You can handle the error here if needed
                    }
                }

                // Connect to the DB2 database
                // Assuming 'SAMPLE' is the name of your database
                sh "sudo -u robo -i db2 connect to SAMPLE"

                // Run the build script
                sh "/QA/LinuxEztBuildScripting/BuildDebugFull.sh"
            }
        }
        stage('Finalization') {
            steps {
                echo 'Finished full rebuild of Debug version of Easytrieve on Linux...'
            }
        }
    }
}

