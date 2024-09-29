import axios from 'axios';
import { useEffect, useState } from 'react';

import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';

import { backend_port } from './constants';
import Dashboard from './dashboard';
import ExtensionProposal from './extension-proposal';
import ResultContainer from './result-container';
import { OurColors } from './theme';

export function isValidUrl(url: string): boolean {
  const urlPattern = new RegExp(
    "^(https?://)?([a-zA-Z0-9-]+\\.)+[a-zA-Z]{2,}(:\\d+)?(/.*)?$"
  );
  return urlPattern.test(url);
}

export default function UrlPasteBar(): JSX.Element {
  const [urlToCheck, setUrlToCheck] = useState<string>();
  const [inputError, setInputError] = useState<string>();
  const [firstScanResult, setFirstScanResult] = useState<boolean>();

  const validateInputUrl = () => {

    handleFirstScan();

  };

  setTimeout(() => setInputError(""), 10000);

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

  console.log({ urlToCheck });

  useEffect(() => {
    // hook to refresh state
    if (urlToCheck === "") {
      setFirstScanResult(undefined);
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
            <Tooltip title="We will search for risks on your website">
              <Button
                variant="contained"
                color="primary"
                onClick={validateInputUrl}
              >
                Analyze
              </Button>
            </Tooltip>
          </div>
        </div>
        <p style={{ color: OurColors.red }}>{inputError}</p>
      </Container>
      {firstScanResult !== undefined && urlToCheck !== undefined && (
        <div>
          <ResultContainer isSafe={firstScanResult} />
          {/*<Dashboard isSafe={firstScanResult} url={urlToCheck} />*/}
        </div>
      )}
      {firstScanResult !== undefined && <ExtensionProposal/>}
    </div>
  );
}
