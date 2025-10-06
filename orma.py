import sys
import os
import zlib
from hashlib import sha1



def help():
    print("orma - a simple version control system")
    print("Commands:")
    print("  init/start               Initialize a new orma repository")
    print("  save <message>          Save the current state with a commit message")
    print("  history                 Show commit history")
    print("  revert <commit-hash>    Revert to a specific commit")
    print("  help                    Show this help message")

    print("  __low level commands__")

    print("  hash-object -w <file>   Hash a file and store it as a blob object")
    print("  cat-file -p <hash>      Display the content of an object")
    print("  ls-tree --name-only <hash> List names of items in a tree object")
    print("  write-tree              Create a tree object from the current directory")
    print("  commit-tree <tree> <parent> <message> Create a commit object")
    

def orma_start():
    if os.path.exists(".orma"):
        print("orma repository already exists")
        return
    os.mkdir(".orma")
    os.mkdir(".orma/objects")
    os.mkdir(".orma/refs")
    os.mkdir(".orma/refs/heads")
    with open(".orma/HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print("Initialized orma repository use help to see commands")


def read_object(sha):
  
    path = f".orma/objects/{sha[:2]}/{sha[2:]}"
    with open(path, 'rb') as f:
        data = zlib.decompress(f.read())
    
    nul_index = data.find(b'\0')
    header = data[:nul_index]
    content = data[nul_index+1:]
    
    obj_type, _ = header.split()
    return obj_type.decode(), content

def checkout_tree(tree_hash, directory="."):
  
    obj_type, tree_data = read_object(tree_hash)
    if obj_type != "tree":
        raise ValueError("Not a tree object")

   

    while tree_data:
        mode_name, tree_data = tree_data.split(b'\0', 1)
        sha_bin = tree_data[:20]
        tree_data = tree_data[20:]
        
        _, name_bin = mode_name.split()
        sha_hex = sha_bin.hex()
        name = name_bin.decode()
        
        obj_type, content = read_object(sha_hex)
        
        path = os.path.join(directory, name)
        if obj_type == "blob":
            with open(path, 'wb') as f:
                f.write(content)
        elif obj_type == "tree":
            os.makedirs(path, exist_ok=True)
            checkout_tree(sha_hex, path)

def orma_revert(commit_hash):
   

    obj_type, commit_content = read_object(commit_hash)
    if obj_type != "commit":
        raise ValueError("Not a commit hash")
        
    tree_line = commit_content.split(b'\n')[0]
    tree_hash = tree_line.split(b' ')[1].decode()
    

    checkout_tree(tree_hash, ".")

    update_head(commit_hash)
    
    print(f"Project reverted. HEAD is now at {commit_hash[:7]}")

def parse_commit(commit_hash):
   
    if not commit_hash or commit_hash == "null":
        return None, None

    obj_type, content = read_object(commit_hash)
    if obj_type != "commit":
        return None, None
    
    parent = None
    message_lines = []
    
    lines = content.split(b'\n')
    for i, line in enumerate(lines):
        if line.startswith(b'parent '):
            parent = line.split(b' ', 1)[1].decode()
        elif line == b'':
            
            message_lines = lines[i+1:]
            break
            
    message = b'\n'.join(message_lines).decode().strip()
    return parent, message

def orma_history():
   
    current_commit = get_head_commit()
    if not current_commit:
        print("No history yet. Make a save first.")
        return

    while current_commit:
        print(f"commit {current_commit}")
        parent, message = parse_commit(current_commit)
        print(f"    {message}\n")
        current_commit = parent
def get_head_commit():

    head_file = os.path.join(".orma", "HEAD")
    if not os.path.exists(head_file):
        return None

    with open(head_file, "r") as f:
        head_content = f.read().strip()
    
    if not head_content.startswith("ref:"):
        return head_content 

    ref_path = head_content.split(" ")[1]
    ref_full_path = os.path.join(".orma", ref_path)

    if not os.path.exists(ref_full_path):
        return None
    
    with open(ref_full_path, "r") as f:
        return f.read().strip()

def update_head(commit_hash):

    head_file = os.path.join(".orma", "HEAD")
    with open(head_file, "r") as f:
        head_content = f.read().strip()
    
    ref_path = head_content.split(" ")[1]
    ref_full_path = os.path.join(".orma", ref_path)

    with open(ref_full_path, "w") as f:
        f.write(commit_hash)

def orma_save(message):

    tree_hash = writeTree(".")
    parent_hash = get_head_commit()

    commit_hash = commit_tree(tree_hash, parent_hash, message)
    
    update_head(commit_hash)
    print(f"Saved snapshot: {commit_hash[:7]} {message}")


def commit_tree(tree_sha, parent_sha, message):
    lines = [f"tree {tree_sha}"]
    if parent_sha:
        lines.append(f"parent {parent_sha}")
    author_info = "vyshnavtr <vyshnavtr0@gmail.com>"
    lines.append(f"author {author_info}")
    lines.append(f"committer {author_info}")
    lines.append(f"\n{message}\n")
    
    content = "\n".join(lines).encode()
    
    return hash_object(content, "commit")

def ls_tree(hash):
    with open(f".orma/objects/{hash[:2]}/{hash[2:]}", "rb") as f:
        data = zlib.decompress(f.read())
        _, tree_data = data.split(b"\x00", maxsplit=1)
        while tree_data:
            mode, tree_data = tree_data.split(b"\x00", maxsplit=1)
            _, name = mode.split()
            print(name.decode("utf-8"))
            tree_data = tree_data[20:]

def hash_object(data, object_type="blob"):

    header = f"{object_type} {len(data)}\0".encode()
    full_data = header + data
    
    sha1_hash = sha1(full_data).hexdigest()
    
    dir_path = f".orma/objects/{sha1_hash[:2]}"
    os.makedirs(dir_path, exist_ok=True)
    with open(f"{dir_path}/{sha1_hash[2:]}", "wb") as f:
        f.write(zlib.compress(full_data))
        
    return sha1_hash


def writeTree(directory="."):
    treeEntries = []
    entries = []

    for entry in os.listdir(directory):
        if entry == ".orma":
            continue
        entryPath = os.path.join(directory, entry)
        entries.append((entry, entryPath))

    entries.sort(key=lambda x: x[0])

    for entryName, entryPath in entries:
        if os.path.isfile(entryPath):
            with open(entryPath, "rb") as f:
                file_content = f.read()
            blobHash = hash_object(file_content,"blob")
            if blobHash:
                mode = "100644"
                treeEntries.append((mode, entryName, blobHash))
        elif os.path.isdir(entryPath):
            subtreeHash = writeTree(entryPath)
            mode = "40000"
            treeEntries.append((mode, entryName, subtreeHash))

    treeContent = b""
    for mode, name, sha1Hex in treeEntries:
        treeContent += mode.encode("ascii") + b" " + name.encode("utf-8") + b"\0"
        sha1Binary = bytes.fromhex(sha1Hex)
        treeContent += sha1Binary

    treeData = b"tree " + str(len(treeContent)).encode("ascii") + b"\0" + treeContent
    treeHash = sha1(treeData).hexdigest()
    compressed = zlib.compress(treeData)
    dirPath = f".orma/objects/{treeHash[:2]}"
    os.makedirs(dirPath, exist_ok=True)
    with open(f"{dirPath}/{treeHash[2:]}", "wb") as f:
        f.write(compressed)
    return treeHash

def main():
    print("Logs from your program will appear here!", file=sys.stderr)
    command = sys.argv[1]
    if command == "init" or command == "start":
         orma_start()

    elif command == "cat-file" and sys.argv[2] == "-p":
        file = sys.argv[3]
        filename = f".orma/objects/{file[:2]}/{file[2:]}"
        with open(filename, "rb") as f:
            data = f.read()
            data = zlib.decompress(data)
            header_end = data.find(b'\x00')
            content = data[header_end + 1:]
            print(content.decode('utf-8'), end="")
    elif command == "help":
        help()
    elif command == "hash-object" and sys.argv[2] == "-w":

        file = sys.argv[3]
        with open(file_path, "rb") as f:
            content = f.read()
        hash = hash_object(content, "blob")
        print(hash)


    elif command == "ls-tree":

        if sys.argv[2] != "--name-only":
            raise RuntimeError(f"Unknown flag {sys.argv[2]}")
        ls_tree(sys.argv[3])

    elif command == "write-tree":
        print(writeTree("."))

    elif command == "commit-tree":
        tree_sha = sys.argv[2]
        parent_sha = sys.argv[3]
        message = sys.argv[4]
        print(commit_tree(tree_sha, parent_sha, message))

    elif command == "save":
        if len(sys.argv) < 3:
            raise RuntimeError("Missing commit message for 'save'")
        orma_save(sys.argv[2])
    elif command == "history":
        orma_history()

    elif command == "revert":
        if len(sys.argv) < 3:
            raise RuntimeError("Missing commit hash for 'revert'")
        orma_revert(sys.argv[2])    
    else:
        raise RuntimeError(f"Unknown command #{command}")


if __name__ == "__main__":
    main()
