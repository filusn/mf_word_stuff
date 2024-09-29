import axios from "axios";
import { useEffect, useState } from "react";

import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

import { backend_port } from "./constants";
import ResultContainer from "./result-container";

export default function UrlPasteBar(): JSX.Element {
  const [urlToCheck, setUrlToCheck] = useState<string>();
  const [firstScanResult, setFirstScanResult] = useState<string>();
  const [translation, setTranslation] = useState<string>();

  const handleFirstScan = () => {
    axios
      .post(backend_port + "analyzeVideo", {
        url: urlToCheck,
      })
      .then((response) => {
        console.log(response.data);
        setFirstScanResult(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  };

  const handleTranslate = () => {
    axios
      .post(backend_port + "translateVideo", {
        text: firstScanResult,
      })
      .then((response) => {
        console.log(response.data);
        setTranslation(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  };

  console.log({ urlToCheck });

  useEffect(() => {
    // hook to refresh state
    if (urlToCheck === "") {
      setFirstScanResult(undefined);
      setTranslation(undefined);
    }
  }, [urlToCheck]);

  return (
    <div>
      <Container style={{ paddingBottom: "3em" }}>
        <Typography variant="h4" style={{ padding: "1em" }}>
          Is this video interesting?
        </Typography>
        <div
          style={{
            display: "flex",
            flexFlow: "row",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <TextField
            id="outlined-basic"
            label="Paste video path here..."
            variant="outlined"
            style={{ width: "40em" }}
            size="small"
            inputProps={{ spellCheck: "false" }}
            onBlur={(e) => {
              setUrlToCheck(e.target.value);
            }}
            onChange={() => setUrlToCheck("")}
          />
          <div style={{ paddingLeft: "0.5em" }}>
            <Tooltip title="We will analyze your video">
              <Button
                variant="contained"
                color="primary"
                onClick={handleFirstScan}
              >
                Analyze
              </Button>
            </Tooltip>
          </div>
        </div>
      </Container>
      {firstScanResult !== undefined && (
        <div>
          <ResultContainer title="Transcription:" message={firstScanResult} />
          <Tooltip title="We will translate transcript to English">
            <Button
              variant="contained"
              color="primary"
              onClick={handleTranslate}
            >
              Translate
            </Button>
          </Tooltip>
          {translation !== undefined && (
            <ResultContainer title="Translation:" message={translation} />
          )}
        </div>
      )}
    </div>
  );
}
