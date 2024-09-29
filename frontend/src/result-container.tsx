import DangerousIcon from '@mui/icons-material/Dangerous';
import LocalPoliceIcon from '@mui/icons-material/LocalPolice';
import { Container, LinearProgress, Typography } from '@mui/material';

import { theme } from './theme';
import { isValidUrl } from './url-paste-bar';

export interface ResultContainerProps {
  readonly isSafe: boolean;
  readonly url: string;
}

export default function ResultContainer(props: ResultContainerProps): JSX.Element {
    const {isSafe, url} = props

    const isValid = isValidUrl(url)
    if (!isValid) return <></>

    const isUrlWithHttp = url.slice(0,4) === 'http'
    const urlWithHttp = isUrlWithHttp ? url : 'http://' + url
    const websiteName = new URL(urlWithHttp).hostname

    const safetyScore = isSafe ? 100 : 25

    const message = isSafe ? `We have scanned ${websiteName} and it's safe!` : `We suspect ${websiteName} is dangerous, better to not shop there.`
    return <Container style={{paddingBottom: '3em'}}>
        <div style={{display: 'flex', flexFlow: 'row', justifyContent: 'center', paddingBottom: '1em'}}>
            <div style={{paddingRight: '0.5em'}}>
                {isSafe ?
                <LocalPoliceIcon color='success' fontSize='large'/> :
                <DangerousIcon color='error' fontSize='large'/>
                }
            </div>
        <Typography variant="h6" style={{color: isSafe ? theme.palette.success.main : theme.palette.error.main}}>{message}</Typography>
        </div>
      <Typography variant="h6" style={{ paddingBottom: "1em" }}>
        Safety score:
      </Typography>
      <div
        style={{ display: "flex", flexFlow: "row", justifyContent: "center" }}
      >
        <div
          style={{
            width: "70%",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <LinearProgress
            variant="determinate"
            value={safetyScore}
            color={isSafe ? "success" : "error"}
            style={{ width: "30%" }}
          />
          <div style={{ paddingLeft: "1em" }}>
            <Typography
              variant="body2"
              color={isSafe ? "success" : "error"}
            >{`${Math.round(safetyScore)}%`}</Typography>
          </div>
        </div>
      </div>
    </Container>
}
