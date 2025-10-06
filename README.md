# Orma: A Conversational Version Control System 🧠

Orma is a simple, Git-like version control system built from scratch in Python. It was created to explore the fundamental concepts behind distributed version control systems like Git. Unlike traditional VCS tools, Orma is designed with a friendly, conversational command-line interface to make version control more intuitive.

The name "Orma" (ഓർമ്മ) is the word for "memory" in Malayalam, reflecting the project's function of remembering a project's history and as a nod to its creator's roots in Kerala, India.

## Key Features

- **Simple, Conversational Commands:** Use intuitive commands like `start`, `save`, and `history`.
- **Git-like Data Model:** Built on the same core principles as Git (blobs, trees, and commits).
- **Local Repository Management:** Full capability to initialize repositories, save snapshots, and view project history locally.
- **Time Travel:** Easily revert your project's state to any previous commit.
- **Built from Scratch:** Written in pure Python with no external libraries, focusing on core concepts.

---

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

- Python 3.x

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/vyshnav-tr/orma-version-control-system.git
    ```
2.  **Navigate to the project directory:**
    ```sh
    cd orma
    ```
3.  **Make the script executable:**
    ```sh
    chmod +x orma.py
    ```

---

## Usage

Orma is designed to be simple and intuitive. Here are the main commands:

- **Initialize a new repository:**
  ```sh
  ./orma.py start