import { Image } from "antd"
import logo from "@/assets/img/chrome.png";

const Avatar = ({ src, alt }: { src: string, alt: string }) => {
  return (
    <div className="avatar" style={{marginRight: 10}}>
      <Image src={src} alt={alt} width={30} fallback={logo} style={{objectFit: 'cover', borderRadius: '50%'}}/>
    </div>
  )
}
export default Avatar