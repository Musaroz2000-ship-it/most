"""Worker entrypoint: discovers every workflow in worker.workflows and runs the worker."""
import asyncio

import mistralai.workflows as workflows


async def main() -> None:
    workflow_classes = workflows.discover_all_workflows_in_package("worker.workflows")
    run_worker = getattr(workflows, "run_worker", None)
    if callable(run_worker):
        await run_worker(workflow_classes)
        return
    from mistralai.workflows.client import get_mistral_client

    client = get_mistral_client()
    await client.workflows.run_worker(workflow_classes)


if __name__ == "__main__":
    asyncio.run(main())
