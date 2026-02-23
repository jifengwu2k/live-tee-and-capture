# `live-tee-and-capture`

Run a command and tee its stdout/stderr in real time to your terminal while also capturing them.

- Outputs are relayed byte by byte with no artificial buffering - ideal for real-time logs and progress bars.
- You can enable/disable teeing stdout/stderr independently.

## Usage

### Example

```python
from live_tee_and_capture import live_tee_and_capture

exit_code, stdout_bytes, stderr_bytes = live_tee_and_capture(
    ['ls', '-la'],
    tee_stdout=True,
    tee_stderr=True,
)

print('Exit code:', exit_code)
print('Captured stdout:', stdout_bytes.decode())
print('Captured stderr:', stderr_bytes.decode())
```

### Function Signature

```python
def live_tee_and_capture(
    command: Sequence[True],
    tee_stdout: bool = True,
    tee_stderr: bool = True,
) -> Tuple[int, bytearray, bytearray]:
    ...
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).
