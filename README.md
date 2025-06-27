# Final Project

**Goal**: assess DevOps skills. This project counts towards your final note.

## Deliverables

- A Continuous Integration (CI) pipeline with the following jobs:
  - Build or download dependencies. Cache the project dependencies.
  - Linter. Use pylint to lint your Python code
  - Dependency security scanning. Ensure there are no vulnerabilities
  - Static security scanning. Ensure there are no vulnerabilities
  - Unit tests
  - Integration tests. Use Docker-based environments in your CI to run the integration tests
  - Artifact signing. Upload the signature file as a **workflow artifact**. You may create your own GPG keypair for this.
  - Generation of SBOM. Upload the SBOM as a **workflow artifact**
  - Test reports should be enabled and configured to capture test data

- An **automated** Continuous Delivery (CD) pipeline with the following jobs:
  - Build Docker image for the application and push it to DockerHub

The order of jobs/blocks are not necessary as listed above. Set up the pipeline following best practices. Remember that fast jobs should run first.

See the **Final project** assignment in the learning platform to learn how to submit your work.

## Resources

You have the following resources at your disposal:

- Application code
- Unit and integration tests for the application
- Docker compose configuration to test locally
- Dockerfile to build the application image

## Tips

- Use Semaphore cache and docker caching to speed up the build
- Use the Sempahore artifact repository to store the signature file and the SBOM
- You need to define the following environment variable in all your CI jobs: `REDIS_PORT=6379`
- In the CI pipeline, use Docker-based environments with the image: `registry.semaphoreci.com/python:3.12.1`
- In the CD pipeline, use the s1-docker self-hosted agent
- You may need to add dependencies to your `requirements.txt`. Use `pip install` to install dependencies and `pip freeze > requirements.txt` to update the requirements file
- Only files in the `app` directory have to pass most tests
- Your GitHub project must be public for Docker builds to work
