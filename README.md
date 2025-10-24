# Final Project

**Goal**: assess DevOps skills. This project counts towards your final note.

## Deliverables

- A Continuous Integration pipeline with the following jobs:
  - Build or download dependencies. Cache the project dependencies (`cache store` and `cache restore`)
  - Linter. Use pylint to lint your Python code
  - Dependency security scanning. Ensure there are no vulnerabilities
  - Generation of SBOM. Upload the SBOM as a **workflow artifact**

- An **automated** Continuous Delivery pipeline with the following jobs:
  - Build Docker image for the application
  - Push application image to DockerHub

- An **automated** Continuous Deployment pipeline with the following jobs:
  - Create a namespace with your name or surname
  - Deploy Docker image to Kubernetes to the namespace (tip: write `deployment.yml`)
  - Wait for rollout
  - Create a service that exposes the application as `nodePort` with a random number between 30000-32767 (tip: write a `service.yml`)

Result: anyone should be able to access your deployed application using `http://devops.tomfern.com:YOUR_CHOSEN_PORT`

See the **Final project** assignment in the learning platform to learn how to submit your work.

## Resources

You have the following resources at your disposal:

- Application code
- Only files in the `src` directory have to pass tests
- Example Kubernetes manifests in `examples` directory
- Your GitHub project must be public

## References

- Past exercises: m01 to m07
- Building Docker images in CI: <https://docs.semaphore.io/using-semaphore/containers/docker>
- Test reports: <https://docs.semaphore.io/using-semaphore/tests/test-reports>
- Semaphore cache: <https://docs.semaphore.io/using-semaphore/cache>
- Semaphore artifacts: <https://docs.semaphore.io/using-semaphore/artifacts>
