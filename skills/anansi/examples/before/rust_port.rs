fn parse_port(input: &str) -> Option<u16> {
    input.parse::<u16>().ok().filter(|port| *port != 0)
}
