# Augment Swebench Agent

Welcome to the **Augment Swebench Agent** repository! This project is part of the Dimvy Clothing Brand's initiative to augment and automate workflows using advanced agent-based technologies.

## 🚀 Overview

The Augment Swebench Agent is designed to enhance software development productivity by integrating with [Swebench](https://github.com/princeton-nlp/SWE-bench) and automating repetitive tasks, error detection, and code management. It aims to provide tools for:

- Automated error fixing and code linting
- Execution and testing of code changes
- Security and vulnerability detection
- Project and codebase management
- Duplicate code detection and resolution

## 🛠️ Features

- **Error Detection & Fixing**: Automatically finds and suggests fixes for common code errors.
- **Execution & Testing**: Runs and verifies code changes in a secure, sandboxed environment.
- **Security Tools**: Scans for vulnerabilities and hides sensitive code from exposure.
- **Code Management**: Supports configuration, project management, and automation tasks.
- **Duplicate Code Finder**: Detects and helps resolve duplicate code segments in the codebase.

## 📦 Installation

Clone this repository:

```bash
git clone https://github.com/Dimvy-Clothing-brand/augment-swebench-agent.git
cd augment-swebench-agent
```

Install dependencies (example shown for Python projects):

```bash
pip install -r requirements.txt
```

Main
You can increase `--num-examples` and `--num-candidate-solutions` to run on more problems and generate more candidate solutions. But be aware that this will take longer and cost more money.

### Command-line Options

- `--num-examples`: Number of examples to run on (default: None, which runs on all examples)
- `--shard-ct`: Number of shards to split the work into (default: 1)
- `--shard-id`: Shard ID to run (0-indexed, default: 0)
- `--num-processes`: Number of processes to use for each example (default: 8)
- `--num-candidate-solutions`: Number of candidate solutions to generate for each example (default: 8)

### Running on more examples.

There are 500 examples total in SWE-bench Verified. Note that this can take awhile, so there are a few levels of parallelism this repository supports.
- Firstly, we suggest running 8 processes. This is the `--num-processes` flag. Beyond this, Docker hits issues.
- Secondly, we support a notion of breaking up the dataset into shards. This is the `--shard-ct` and `--shard-id` flags. This makes it relatively easy to split up the work across multiple machines, which circumnvents the issues with scaling Docker beyond 8 processes.

In our experiments, it took us a couple hours to run the full evaluation for 1 candidate solution per problem. This was
with 10 shards split out across separate pods (managed by Kubernetes) and each pod had 8 processes.

Keep in mind that you may hit rate-limits from Anthropic running 80 agents in parallel like we did. We have very high rate-limits with Anthropic's API that you may not have. Given this, you may have to run with a smaller `--shard-ct` and/or `--num-processes`.

Suppose you want to run with 10 shards and 8 processes per shard, then that would mean you run the following command 10 times, varying the `--shard-id` flag from 0 to 9, on 10 different machines:
```bash
python run_agent_on_swebench_problem.py --shard-ct 10 --shard-id <worker_index> > logs.out 2> logs.err
```

### Majority Vote Ensembler

The Majority Vote Ensembler is a tool that helps select the best solution from multiple candidates using an LLM. It works by presenting multiple candidate solutions to a problem to OpenAI's o1 model and asking it to analyze and select the most common solution.

#### How It Works
=======
> **Note:** Make sure to check the specific dependencies and environment requirements in the `requirements.txt` or project documentationmain

## ⚡ Usage

You can run the agent using the following command (modify as per your main entry point):

```bash
python main.py
```

For advanced configuration, see the `config/` directory or refer to the project documentation.

## 🔒 Security

- The agent includes security checks to prevent code injection and data leaks.
- Sensitive code and credentials should be stored in `.env` files or secured configuration.
- Always review and test automated fixes before deploying to production.

## 💬 Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Commit your changes and open a pull request.

Please refer to the `CONTRIBUTING.md` (or open an issue for guidelines if not present).

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📧 Contact

For project inquiries or paid collaborations, please contact:  
**Email:** contact@dimvyclothing.com  
**GitHub:** [Dimvy-Clothing-brand](https://github.com/Dimvy-Clothing-brand)

---

> *Empowering developers, automating excellence.*
