import { Container, Typography } from "@mui/material";

import { theme } from "./theme";

export interface ResultContainerProps {
  readonly title: string;
  readonly message: string;
}

export default function ResultContainer(
  props: ResultContainerProps
): JSX.Element {
  const { title, message } = props;

  return (
    <Container style={{ paddingBottom: "3em" }}>
      <Typography
        variant="h4"
        style={{
          textAlign: "center",
          paddingBottom: "1em",
          fontWeight: "bold",
        }}
      >
        {title}
      </Typography>
      <div
        style={{
          display: "flex",
          flexFlow: "row",
          justifyContent: "center",
          paddingBottom: "1em",
        }}
      >
        <Typography
          variant="h6"
          style={{
            color: theme.palette.success.main,
            textAlign: "justify",
          }}
        >
          {message}
        </Typography>
      </div>
      <Typography variant="h6" style={{ paddingBottom: "1em" }}></Typography>
      <div
        style={{ display: "flex", flexFlow: "row", justifyContent: "center" }}
      ></div>
    </Container>
  );
}
