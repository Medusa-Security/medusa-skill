fn parse_port(input: &str) -> Option<u16> {
    // Parsing as u16 rejects out-of-range values; zero is filtered out because it is not a usable port.
    input.parse::<u16>().ok().filter(|port| *port != 0)
}
